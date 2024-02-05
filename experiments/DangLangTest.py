from dash import Dash, dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

import os

prompt = ChatPromptTemplate.from_template("tell me a joke about {foo}")
api_key = os.environ["OPENAI_API_KEY"]
model = ChatOpenAI(openai_api_key=api_key,model="gpt-3.5-turbo-0125")
chain = prompt | model

app = Dash()

app.layout = html.Div([
   html.H1("Joke-Generating App"),
   html.Label("Tell me a joke about: "),
   dcc.Input(id='subject', debounce=True, maxLength=18),
   dbc.Button(id="ok-button",children="OK",n_clicks=0),
   html.Hr(),
   html.Div(id='joke-placeholder')
])

@callback(
   Output('joke-placeholder', 'children'),
   Input('ok-button','n_clicks'),
   State('subject', 'value'),
   prevent_initial_call=True
)
def update_layout(btn_clicks,joke_topic):
   print(f"Ran this invocation {btn_clicks}")
   joke = chain.invoke({"foo": joke_topic},)
   output = joke.content
   return output


if __name__ == "__main__":
   app.run_server(debug=True)