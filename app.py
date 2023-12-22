'''
 # @ Create Time: 2023-12-21 14:24:36.280001
'''

import pandas as pd
import dash
from dash.dependencies import Input, Output
from dash import dcc, html, dash_table, State
import plotly.express as px
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
import nltk
from nltk.corpus import stopwords
import string

app = Dash(__name__, title="bible_app")

df = pd.read_csv('/Users/asgermollernielsen/Downloads/bible_data.csv', encoding='utf-8')
df.rename(columns={"Language": "language", 'Bible edition':'bible_edition', 'Book name':'book_name', 'Chapter':'chapter','Verse':'verse'}, inplace=True)
df.columns
data=df
#stopwords = open('stopwords.txt',encoding='utf-8').read().split("\n")  #Alternative list of english stopwords, but 'from nltk.corpus import stopwords' is used as it covers many languages.

# app.layout = html.Div(style={'backgroundColor': 'red'},  # Set the background color
#         children=[     #Start of html/app/dashboard layout section.

app.layout = html.Div([     #Start of html/app/dashboard layout section.
        html.H1("Bible Editions (Group 9)", style={"textAlign":"center"}),  #Dashboard main header.
        html.Div([      
                
            
        # Components for task 1:    
        html.H2("Task 1: Bar Chart"),
        html.H4("Select Bible LANGUAGE and EDITION:"),
            dcc.Dropdown(   
                id='id_language1',  #ID used for CALLBACK.
                options=[{'label': i.upper(), 'value': i} for i in data['language'].unique()],  #Dropdown options based on unique 'languges' from data.
                value=data['language'].unique()[0]),    #Index 0 in 'language' is shown as default.
           
            dcc.Dropdown(   
                id='id_bible_edition1', #ID used for CALLBACK.
                options=[],     #Dropdown options based on CALLBACK from 'id_language1' above.
                value=data['bible_edition'].unique()[0]),   #Index 0 in 'bible_edition' is shown as default.   

            dcc.Graph(  #Graph component for barchart
                id = 'id_bar_chart',),  #ID used for Bar Chart CALLBACK
        
            
        # Components for task 2:    
        html.H2("Task 2: Search for keyword to display textual word cloud summary"),
        html.H4("Search for a keyword and press the 'Enter' key and wait for a couple of seconds:"),  
            dcc.Input(id='id_keyword-input', type='text', placeholder='Enter keyword', debounce=True), #Setting 'debounce=True' helps in delaying the execution of the callback function until a certain period of inactivity from the user,
            html.Div(style={'margin-top': '10px'}), #Margin between search field and wordcloud.
            
            html.Img(id='id_image_wc'),    #ID used for word cloud CALLBACK
        html.Div(style={'margin-top': '100px'}),    #Margin below component   
        
        
        # Components for task 3:    
        html.H2("Task 3: Search for Bible verses containing all search words"),
        html.H4("Search for one or more words and press the 'Enter' key:"),    
            dcc.Input(id='id_allkeywords_input', 
                      type='text', 
                      style={'width':'500px'},  #Width / length of search field.
                      placeholder='In the beginning God created....'), 
            
            dash_table.DataTable(id='id_table3',
                                 columns=[{'name': 'Bible Edition', 'id': 'bible_edition'}, #Column 'names' and 'ids' from data.
                                          {'name': 'Book Name', 'id': 'book_name'},
                                          {'name': 'Chapter', 'id': 'chapter'},
                                          {'name': 'Verse', 'id': 'verse'}],
                                 page_current=0,    #Start page
                                 page_size=10,      #Max views/lines in table
                      style_cell={'textAlign': 'left'},
                      style_table={'overflowX': 'auto'}),   #This enables scrolling within the table when the content exceeds the specified width.
        html.Div(style={'margin-top': '100px'}),    #Margin below component
                
        
        # Components for task 4:
        html.H2("Task 4: Show corresponding verses for all Bible editions"),
        html.H4("Select Bible 'Language', 'Book, 'Chapter' and 'Verse number':"),
            dcc.Dropdown(
                id='id_language4',
                options=[{'label': i.upper(), 'value': i} for i in data['language'].unique()],
                placeholder='Select Language'),
                   
            dcc.Dropdown(
                id='id_book_name4',
                options=[],
                placeholder='Select Book'),
       
            dcc.Dropdown(
                id='id_chapter4',
                options=[],
                placeholder='Select Chapter'),
            
            dcc.Dropdown(
                id='id_verse4',
                options=[],
                placeholder='Select Verse'),
         
            dash_table.DataTable(id='id_table4',
                                 columns=[{'name': 'Language', 'id': 'language'},   #Column 'names' and 'ids' from data.
                                          {'name': 'Bible Edition', 'id': 'bible_edition'},
                                          {'name': 'Book Name', 'id': 'book_name'},
                                          {'name': 'Chapter', 'id': 'chapter'},
                                          {'name': 'Verse', 'id': 'verse'}],
                                 page_current=0,    #Start page
                                 page_size=10,      #Max views/lines in table
                      style_cell={'textAlign': 'left'},
                      style_table={'height': '300px', 'overflowY': 'auto'}),   #This enables scrolling within the table when the content exceeds the specified height of 300 pixels.
        html.Div(style={'margin-top': '100px'}),    #Margin below component
        ]),
])  #End of html/app/dashboard layout section.

        

##### CALLBACK SECTION #####
#Callback functions makes the html interactive depending on selection in Dropdowns etc.:

# Callback for task 1:   
@app.callback(      #First dropdown1:
    Output(component_id='id_bible_edition1', component_property='options'),
    Input('id_language1','value'))
def select_language1(language):
    language = data[data['language'] == language]   #Filters data equal to selected language
    return [{'label': i, 'value': i} for i in language['bible_edition'].unique()]   #Returns unique bible editions based on selected language to dropdown below. 

@app.callback(      #Second dropdown2, dependent on dropdown1:
    Output('id_bible_edition1','value'),
    Input('id_bible_edition1','options'))
def select_bible_edition1(bible_edition):
    return [edition['value'] for edition in bible_edition][0]  #Returns selected bible edition, default index-0. 

@app.callback(      #Bar chart, dependent on dropdown1 and dropdown 2, including chapter counter:
    Output('id_bar_chart','figure'),
    Input('id_language1','value'),
    Input('id_bible_edition1','value'))
def bar_chart1(selected_language, selected_bible_edition):       
    filtered_data = data[(data['language'] == selected_language) & (data['bible_edition'] == selected_bible_edition)]   #Filters data depending on selected 'language' AND 'bible_edition'.
    chapters_per_book = filtered_data.groupby('book_name')['chapter'].nunique().reset_index()   #Groups the 'data' by the 'book_name' column and selects the 'chapter' column. 
                                                                                                #After grouping, 'nunique()' calculates the number of unique values for each group in the 'chapter' column within each book group.
                                                                                                #'reset_index()' converts the computed values and book names into a new DataFrame, where the book names become a column, and the unique chapter counts become another column.
    fig = px.bar(chapters_per_book, x='book_name', y='chapter',
                 labels={'chapter': 'Number of Chapters'}, 
                 title=f'Number of Chapters pr. Book for: {selected_language.upper()}, {selected_bible_edition}')
    fig.update_layout(xaxis={'title': 'Book Name'}, yaxis={'title': 'Number of Chapters'}, title_x=0.5)
    return fig 
   
 

# Callback for task 2:       
@app.callback( #Task 2, search for keyword and create textual summary:
     Output('id_image_wc', 'src'),             #The 'src' attribute specifies the URL or the source of an image, audio, video, iframe, etc., to be displayed within an HTML element.
     [Input('id_keyword-input', 'n_submit')],  #'n_submit' triggers execution of the Input by pressing 'Enter'.
     [State('id_keyword-input', 'value')])     #'State' prevents the CALLBACK from executing before 'n_submit' is executed.
def update_wordcloud(n_submit, keyword):
     n_submit = n_submit or 0   #When in 'waiting' mode. 
     if n_submit > 0:           #When 'Enter' is pressed.
         if not keyword:
             text = ' '.join(data['verse'])
         else:
             filtered_data = data[data['verse'].str.contains(keyword, case=False, na=False)]    #Looking for 'keyword' in 'verse', not case-sensetive and not considering missing values. 
             t = ' '.join(filtered_data['verse'])   #Concatenates the 'verse' in filtered_words list into a single string with space (' ') as separator.
             words = nltk.word_tokenize(t)  #Splits the input text into a list of words.
             stop_words = set(stopwords.words('english', 'spanish'))    #Avalible stopwords languages.
             punctuation = set(string.punctuation)  # The variable punctuation will contain a set of punctuation characters (, .  ! etc.).
             filtered_words = [word.lower() for word in words if word.lower() not in stop_words and word.lower() not in punctuation]    #Filters words that are not a 'stopword' or 'punctuation'.
             text = ' '.join(filtered_words)    #Concatenates the elements of the filtered_words list into a single string with space (' ') as separator. 
         
         wordcloud = WordCloud(width=1200, height=400, background_color='white').generate(text)     #Generate word cloud.
        
         img_path = 'wordcloud.png'   #Create a .png image.
         wordcloud.to_file(img_path)  #Store .png image in folder.
         encoded_image = base64.b64encode(open(img_path, 'rb').read()).decode('utf-8')  #decode .png image from 'base64' to 'utf-8' for more suitable use in .html.
         
         import os
         os.remove(img_path)    #Removes the created .png image in the folder.

         return f'data:image/png;base64,{encoded_image}'   #Return image to Output('id_image_wc', 'src') in dashboard.



# Callback for task 3: 
@app.callback(
    Output('id_table3', 'data'),
    [Input('id_allkeywords_input', 'n_submit')],
    [State('id_allkeywords_input', 'value')])
def table3(n_submit, keyword):
    n_submit = n_submit or 0   #When in 'waiting' mode.
    if n_submit >= 1:   #When 'Enter' is pressed.
        if not keyword:
            return data.to_dict('records')

        keywords_list = keyword.lower().split()         # Split and convert keywords to lowercase
        filtered_data = data.dropna(subset=['verse'])   # Drop rows with NaN in 'verse' column
     
        for word in keywords_list:
            regex_pattern = r'(?:(?<=\s)|(?<=^)){}(?=\s|$)'.format(re.escape(word)) # Filter data for rows containing all the keywords as whole words: in the beginning or end of the line or separated by spaces
            filtered_data = filtered_data[filtered_data['verse'].str.contains(regex_pattern, case=False, regex=True)]   #Looking for 'keyword' in 'verse', not case-sensetive, not considering missing values and not considering keyword order.
            unique_filtered_data = filtered_data[['bible_edition', 'book_name', 'chapter', 'verse']].drop_duplicates()
            
        return unique_filtered_data.to_dict('records')      #This method '.to_dict' converts the data into a list of dictionaries.
    
    else:
        return data.to_dict('records')


# Callback for task 4:
@app.callback(      #Language, first dropdown1:
    Output('id_book_name4','options'),
    Input('id_language4','value'))
def select_language4(language):
    language = data[data['language'] == language]
    return [{'label': i, 'value': i} for i in language['book_name'].unique()]   #Returns unique 'book names' based on selected language to dropdown below.
    
@app.callback(      #Book Name, third dropdown3 - dependent on dropdown 1 and 2:
    Output('id_chapter4','options'),
    Input('id_book_name4','value'))
def select_book4(book_name):
    book_name = data[data['book_name'] == book_name]
    return [{'label': i, 'value': i} for i in book_name['chapter'].unique()]    #Returns unique 'chapter' based on selected book name to dropdown below.

@app.callback(      #Chapter, forth dropdown4 - dependent on dropdown 1, 2 and 3:
    Output('id_verse4','options'),
    Input('id_chapter4','value'))
def select_chapter4(chapter):
    data['verse_number'] = data['verse'].str.extract(r'^(\d+)(?= )')    #Finds the 'verse number'.
    data_verse_number = data[data['verse_number'].notnull()]            #Removes empty fields, NaN etc
    verses = data_verse_number[data_verse_number['chapter'] == chapter]['verse_number'].unique()
    return [{'label': verse_number, 'value': verse_number} for verse_number in verses]  #Returns unique 'verse number' based on selected chapter.

@app.callback(
    Output('id_table4', 'data'),
    Input('id_language4', 'value'),
    Input('id_book_name4', 'value'),
    Input('id_chapter4', 'value'),
    Input('id_verse4', 'value'))
def update_table(language, book, chapter, verse):
    data['verse_number'] = data['verse'].str.extract(r'^(\d+)(?= )')    #Finds the 'verse number'.
    data_verse_number = data[data['verse_number'].notnull()]            #Removes empty fields, NaN etc.
    
    filtered_data = data_verse_number.copy()
    
    if language:
        filtered_data = filtered_data[filtered_data['language'] == language]    #Filters data to match the 4 dropdown inputs.
    if book:
        filtered_data = filtered_data[filtered_data['book_name'] == book]
    if chapter:
        filtered_data = filtered_data[filtered_data['chapter'] == chapter]
    if verse:
        filtered_data = filtered_data[filtered_data['verse_number'] == verse]

    return filtered_data.to_dict('records')     #This method '.to_dict' converts the data into a list of dictionaries.
        

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
