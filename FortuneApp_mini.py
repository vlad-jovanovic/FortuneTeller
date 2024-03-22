from dash import Dash, dcc, html, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from datetime import datetime, date

import os, json, random

# Two global parameters when running
USE_AI = False
WILL_RUN_LIVE = False

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

with open("./assets/astrology.json") as json_file:
    astrology_data = json.load(json_file)

# Layout: far right for buttons, panel from left, rest of screen (three cards on top) and bottom has overarching fortune

# Basic information
min_length_desire = 10
input_birthdate = dbc.InputGroup([dbc.InputGroupText("Birthdate"),dcc.DatePickerSingle(id="input_birthdate",min_date_allowed=date(1000,1,1),max_date_allowed=datetime.today(),date=datetime.today(),persistence=True,persistence_type="local",persisted_props=["date"])],className="mb-3")
input_desired_fortune = dbc.InputGroup([dbc.InputGroupText("Your question (use I statements and first-person)"),dbc.Input(id="input_desired_fortune",debounce=True,type="text",persistence=True,persistence_type="local",persisted_props=["value"],minlength=min_length_desire)],className="mb-3")
# Use a list to go for it

listgroup_input = dbc.ListGroup([
   dbc.ListGroupItem(input_birthdate),
   dbc.ListGroupItem(input_desired_fortune),
],flush=True)


# Buttons for interaction
button_phrase = "Tell Me My Fortune!"
button_fortune_sequence = dbc.Button(button_phrase,id="button_fortune_sequence",disabled=False,n_clicks=0)
# Layout container for the buttons: dbc.Col()
column_buttons = dbc.Col([button_fortune_sequence],id="column_buttons",width=12,style={"border":"1px solid #000","padding":"10px"})

# Overarching fortune spot
paragraph_fortune = html.P(["Your future fortune"],id="paragraph_fortune")
column_fortune = dbc.Col([paragraph_fortune],id="column_fortune",width=12,style={"border":"1px solid #000","padding":"20px"})

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
         dbc.CardImg(src="./assets/tarot_card_placeholder.jpeg",id=f"image_card_{card['id']}"),
         dbc.CardFooter([html.H4("",className="card-title",id=f"title_card_name_{card['id']}"),html.P("",className="card-subtitle",id=f"body_card_fortune_{card['id']}")]),
      ],className="mx-auto") for card in chosen_spread["card_description"] # End of children of stack
   ],direction="vertical",gap=3), # End of stack
],id="column_spread",width=12,style={"border":"1px solid #000","padding":"10px"})

# Set up everything for the openAI model
print("Prompt chosen...")
print(chosen_spread["prompt"].format(*chosen_spread["prompt_terms"]))
prompt = ChatPromptTemplate.from_template(chosen_spread["prompt"].format(*chosen_spread["prompt_terms"]))
api_key = os.environ["OPENAI_API_KEY"]
model = ChatOpenAI(openai_api_key=api_key,model="gpt-4-0125-preview")#"gpt-3.5-turbo-0125")
chain = prompt | model

app.layout = html.Div([
   listgroup_input,
   dbc.Row([
      column_buttons,
      column_spread,
      column_fortune,
   ],justify="center", align="center"), # Row that contains everything
])#,style={"height":"100vh"}) # Div that contains everything

@callback([Output("button_fortune_sequence","children"),
           Output("button_fortune_sequence","disabled")],
          Input("button_fortune_sequence","n_clicks"),
          [State("input_birthdate","date"),State("input_desired_fortune","value")],prevent_initial_call=True)
def callback_fortune_button_press(n_clicks,birthdate,desire):
   if n_clicks <= 0:
      return no_update
   if birthdate is None:
      return ["ERROR: Bad birthdate :(",False]
   if desire is None:
      return ["ERROR: No question entered.",False]
   if len(desire) <= min_length_desire:
      return [f"ERROR: Need minimum {min_length_desire} characters.",False]
   return [dbc.Spinner(size="sm",type="grow"), " Divining..."],True

# If it becomes a spinner then chose the cards that will be represented
@callback([Output(f"image_card_{card['id']}","src") for card in chosen_spread["card_description"]]+
          [Output(f"image_card_{card['id']}","alt") for card in chosen_spread["card_description"]]+
          [Output(f"image_card_{card['id']}","title") for card in chosen_spread["card_description"]]+
          [Output(f"title_card_name_{card['id']}","children") for card in chosen_spread["card_description"]],
           Input("button_fortune_sequence","children"),prevent_initial_call=True)
def callback_draw_cards(btn_child):
   if btn_child ==  button_phrase or btn_child == "" or (type(btn_child)==str and btn_child.startswith("ERROR")):
      return no_update
   # Then draw three cards from 0 to 77?
   sampled_numbers = random.sample(list(range(len(card_deck))),chosen_spread["spread_count"])
   # Get the images to be shown for this
   src_list = [""]*chosen_spread["spread_count"]
   title_list = [""]*chosen_spread["spread_count"]
   alt_list = [""]*chosen_spread["spread_count"]
   for idx in range(chosen_spread["spread_count"]):
      card_number = sampled_numbers[idx]
      card_name = card_deck[card_number]["name"]
      # To store
      title_list[idx] = card_name
      alt_list[idx] = card_number
      # Create the name of each image order_name_of_card.jpg
      src_list[idx] = f"./assets/cardfaces/fullimages/{card_deck[card_number]["ordering"]}_{card_name.replace(" ","_")}.jpg"
   # Name of the cards will be in the title list and the title card name
   return src_list+alt_list+title_list+title_list

# Cards have been chosen...no input all the information
# f"body_card_fortune_{card['id']}" for the card body
# prompt and prompt terms
@callback([Output(f"body_card_fortune_{card['id']}","children") for card in chosen_spread["card_description"]]+
          [Output("paragraph_fortune","children"),
           Output("button_fortune_sequence","children",allow_duplicate=True),
           Output("button_fortune_sequence","disabled",allow_duplicate=True)],
          Input(f"title_card_name_0","children"),
          [State("input_birthdate","date"),State("input_desired_fortune","value")]+
          [State(f"image_card_{card['id']}","title") for card in chosen_spread["card_description"]]
          ,prevent_initial_call=True)
def callback_pull_fortune(forget,birthdate,desire,*card_names):
   if forget is None or forget == "":
      card_fortune = ["Fortune is unknown..."]*chosen_spread["spread_count"]
      paragraph_fortune = ["Fortune is unknown... to say"]
      button_response = ["...Try Again?",False]
      return card_fortune+paragraph_fortune+button_response
   # Get the age and sign...
   age, sign = calculate_age_and_zodiac(birthdate)
   if age is None or sign is None:
      card_fortune = ["Fortune is unknown..."]*chosen_spread["spread_count"]
      paragraph_fortune = ["Fortune is unknown... to say"]
      button_response = ["Birthdate input incorrect...Try Again?",False]
      return card_fortune+paragraph_fortune+button_response
   prompt_sequence = {name: "" for name in chosen_spread["prompt_terms"]}
   prompt_sequence["age"] = age
   prompt_sequence["sign"] = sign
   prompt_sequence["desire"] = desire
   for card,idx in zip(card_names,range(chosen_spread["spread_count"])):
      prompt_sequence[f"card-{idx}"] = card
   print(f"Prompt sequence:\n\t{prompt_sequence}")
   # Now go for the API access
   print("Fortune:")
   if USE_AI:
      fortune_model = chain.invoke(prompt_sequence)
      paragraphs = fortune_model.content.split("\n\n")
      if len(paragraphs) != chosen_spread["spread_count"]+1: # With overall fortune
         print(f"Could not fit fortune with {len(paragraphs)}:")
         for i,para in enumerate(paragraphs,start=0):
            print(f"{i}\t{para}")
         card_fortune = ["Fortune is complicated...scroll down..."]*chosen_spread["spread_count"]
         paragraph_fortune = [fortune_model.content]
         button_response = ["A complex fortune...scroll to the very bottom.",True]
         return card_fortune+paragraph_fortune+button_response 
   else:
      placeholder = "1\n\n2\n\n3\n\n4"
      # Now take this and break it up into four parts
      paragraphs = placeholder.split("\n\n")
   for i,para in enumerate(paragraphs,start=0):
      print(f"{i}\t{para}")
   return paragraphs+["Fortune below...refresh for a new chance",True]

def convert_month(month_string):
   return datetime.strptime(month_string,"%B").month

def calculate_age_and_zodiac(birthdate):
   '''Figure out what the age and zodiac is based on the birthdate entered.'''
   
   try:
      date_part = birthdate.split("T")[0]
      birthdate_dt = datetime.strptime(date_part, "%Y-%m-%d")
      today = datetime.today()
      age = today.year - birthdate_dt.year - ((today.month, today.day) < (birthdate_dt.month, birthdate_dt.day))
      
      # Determine the astrological sign
      for sign, date_range in astrology_data["Zodiac"].items():
         start_date, end_date = date_range["Dates"].split(" - ")

         start_month, start_day = start_date.split()
         end_month, end_day = end_date.split()
         
         if (birthdate_dt.month, birthdate_dt.day) >= (convert_month(start_month), int(start_day)) and (birthdate_dt.month, birthdate_dt.day) <= (convert_month(end_month), int(end_day)):
            zodiac_sign = sign
            break
      else:
         zodiac_sign = "Invalid Date"

      return age, zodiac_sign
   except Exception as e:
      print(e)
      return None, None

if __name__ == "__main__":
   import sys
   if "live" in sys.argv: 
      print("Running live.")
      WILL_RUN_LIVE = True
   else:
      print("Running debug.")
      WILL_RUN_LIVE = False

   if "ai" in sys.argv:
      print("Using AI.")
      USE_AI = True
   else:
      print("Using filler data.")
      USE_AI = False

   if WILL_RUN_LIVE:
      app.run_server(debug=False,host='0.0.0.0',port=8050)
   else:
      app.run_server(debug=True,port=8050)