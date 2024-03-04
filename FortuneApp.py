from dash import Dash, dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from datetime import datetime, date

import os, json

app = Dash(__name__,external_stylesheets=[dbc.themes.CERULEAN])

# Load up the tarot deck information with keys as an array of dictionaries with keys:
'''
ordering <int>: (0-77),
arcana <string>: ("Major Arcana","Wands","Cups","Swords","Pentacles"),
name <string>: strings with capitals and spaces,
'''
with open('./assets/tarot_deck_numbered.json','r') as tart_deck_location:
   # parse_int uses a lambda function (i.e. anonymous function)
   card_deck = json.load(tart_deck_location, parse_int=lambda id: int(id) if id.isnumeric() else id)

# Layout: far right for buttons, panel from left, rest of screen (three cards on top) and bottom has overarching fortune

# Basic information
#input_name = dbc.InputGroup([dbc.InputGroupText("Your name"),dbc.Input(id="input_name",debounce=True,type="text",persistence=True,persistence_type="local",persisted_props=["value"])],className="mb-3",)
input_birthdate = dbc.InputGroup([dbc.InputGroupText("Birth date"),dcc.DatePickerSingle(id="input_birthdate",min_date_allowed=date(1924,1,1),max_date_allowed=datetime.today(),date=datetime.today(),persistence=True,persistence_type="local",persisted_props=["date"])],className="mb-3")
#input_gender = dbc.InputGroup([dbc.InputGroupText("Your gender"),dbc.Input(id="input_gender",debounce=True,type="text",persistence=True,persistence_type="local",persisted_props=["value"])],className="mb-3")
input_desired_fortune = dbc.InputGroup([dbc.InputGroupText("Your question (use I statements and first-person)"),dbc.Input(id="input_desired_fortune",debounce=True,type="text",persistence=True,persistence_type="local",persisted_props=["value"])],className="mb-3")
# Offcanvas for all basic information
offcanvas_input = dbc.Offcanvas([
   input_birthdate,
   input_desired_fortune,
],id="offcanvas_input",title="Please tell me who you are...",is_open=False)


# Buttons for interaction
button_input_offcanvas = dbc.Button("Who I am",id="button_input_offcanvas",disabled=False,n_clicks=0)
button_fortune_sequence = dbc.Button("Fortune Sequence",id="button_fortune_sequence",disabled=True,n_clicks=0)
# Layout container for the buttons: dbc.Col()
column_buttons = dbc.Col([button_input_offcanvas,button_fortune_sequence],id="column_buttons",width=2,style={"border":"1px solid #000","padding":"10px"})

# Overarching fortune spot
paragraph_fortune = html.P(["Your future fortune"],id="paragraph_fortune")
column_fortune = dbc.Col([paragraph_fortune],id="column_fortune",width=10,style={"border":"1px solid #000","padding":"10px"})

# Load up the tarot spread(s) as an array of dictionaries with keys:
'''
name <string>: name of the spread,
prompt <string>: the f-string to send,
prompt_terms <array of strings>: list of names for each of hte inputs into f-string (should all be strings),
fortune_sequence <array of strings>: the sequence that should go on the fortune button and what should be displayed 
spread_count <int>: number of cards that will be in the spread,
card_description <array of dictionaries>: This contains an array witha a description of what each of the cards means,
   id <int>: card position and index,
   name <string>: name of the position,
   description <string>: String to show description,
'''
with open('./assets/tarot_spreads.json','r') as tarot_spreads_location:
   tarot_spreads = json.load(tarot_spreads_location, parse_int=lambda id: int(id) if id.isnumeric() else id)
index_chosen_spread = 0 # Future work will have a drop down for this to have dynamic generation of card spread location
chosen_spread = tarot_spreads[index_chosen_spread]

# Create spot for each card
column_spread = dbc.Col([
   dbc.Stack([
      dbc.Card([
         dbc.CardHeader([html.H4(card["name"],className="card-title"),html.P(card["description"],className="card-subtitle")]),
         dbc.CardImg(src="./assets/tarot_card_placeholder.jpeg",id=f"image_card_{card['id']}",style={"max-width":"200px"}),
         dbc.CardFooter([html.H4("",className="card-title",id=f"title_card_name_{card['id']}"),html.P("",className="card-subtitle",id=f"body_card_fortune_{card['id']}")]),
      ],style={"max-width":"400px"},className="mx-auto") for card in chosen_spread["card_description"] # End of children of stack
   ],direction="horizontal",gap=3), # End of stack
],id="column_spread",width=10,style={"border":"1px solid #000","padding":"10px"})

app.layout = html.Div([
   dbc.Row([
      dbc.Col([
         dbc.Row([
            column_spread,
         ],justify="center", align="center", className="mb-3",style={"height": "66.6667%"}), # Row that contains the column spread
         dbc.Row([
            column_fortune,
         ],justify="center", align="center", className="mb-3", style={"height": "33.3333%"}), # Row that contains the fortune
      ],width=10,style={"height":"100vh"}), # Column that contains spread and fortune
      column_buttons,
   ]), # Row that contains everything
   offcanvas_input,
],style={"height":"100vh"}) # Div that contains everything

@callback(Output("offcanvas_input","is_open"),Input("button_input_offcanvas","n_clicks"))
def callback_button_input_press(n_clicks):
   if n_clicks > 0:
      return True
   else:
      return False


if __name__ == "__main__":
   app.run_server(debug=True)