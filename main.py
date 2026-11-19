from dataclasses import dataclass
from drafter import *


# Each Game object stores information about one game the user owns.
@dataclass
class Game:
    name: str
    genre: str
    completed: bool
    description: str


# State stores information that must be remembered between website routes.
@dataclass
class State:
    games: list[Game]
    recommended_games: list[Game]
    selected_genre: str
    completion_filter: str
    message: str


# The following route represents the homepage of Game Selector
@route
def index(state: State) -> Page:
    return Page(state, [
        Header("Game Selector"),
        "Find something to play from the games you already own.",
        state.message,
        
        Button("View Game Library", "library"),
        Button("Add a Game", "add_game"),
        Button("Set Preferences", "preferences"),
        Button("Get Recommendations", "recommended_game")
    ])


# This extra route provides another way to reach the homepage.
@route("home_page")
def home_page(state: State) -> Page:
    return index(state)


# Shows the games in the user's library.
@route
def library(state: State) -> Page:
    page_content = [
        Header("Your Game Library")
        ]
        
    if not state.games:
        page_content.append("Your library is empty. Add a game to get started.")
        page_content.append(Button("Add a Game", "add_game"))
    else:
        for game in state.games:
            page_content.append(game.name)
            page_content.append("Genre: " + game.genre)

            if game.completed:
                page_content.append("Status: Completed")
            else:
                page_content.append("Status: Unfinished")

            page_content.append("Description: " + game.description)

    page_content.append(Button("Remove a Game", "remove_game_page"))
    page_content.append(Button("Home", "index"))

    return Page(state, page_content)


# The Add Game page asks only for details about the game being added.
# The genre here describes the game; it is not the user's preferred genre.
@route
def add_game(state: State) -> Page:
    return Page(state, [
        Header("Add a Game to Your Library"),
        "Game name:",
        TextBox("game_name"),
        "Genre of this game:",
        SelectBox("game_genre", [
            "Action", "Adventure", "Puzzle", "RPG",
            "Racing", "Shooter", "Simulation", "Sports", "Strategy", "Other"
        ]),
        
        "Have you completed this game?",
        CheckBox("completed"),
        
        "Short description:",
        TextArea("description"),
        
        Button("Save Game", "save_game")
    ])


# Saves the submitted game details in State.games.
@route
def save_game(state: State, game_name: str, game_genre: str,
              completed: bool, description: str) -> Page:
    """
    .strip() is used to prevent errors if only spaces are typed in. 
    """
    cleaned_name = game_name.strip()

    if cleaned_name == "":
        state.message = "Please enter a game name. No game was added."
    else:
        new_game = Game(cleaned_name, game_genre, completed, description.strip())

        # Add the new Game to the existing list.
        state.games.append(new_game)
        state.message = cleaned_name + " was added to your library."

    return library(state)


# This page contains the form for removing a game.
@route
def remove_game_page(state: State) -> Page:
    return Page(state, [
        Header("Remove a Game"),
        "Enter the exact name of the game you want to remove:",
        TextBox("game_to_remove"),
        
        Button("Remove Game", "remove_game")
    ])


# Removes the first game whose name matches the entered name.
@route
def remove_game(state: State, game_to_remove: str) -> Page:
    cleaned_name = game_to_remove.strip()
    found_game = False

    if cleaned_name == "":
        state.message = "Enter a game name before selecting Remove Game."
    else:
        remaining_games = []

        for game in state.games:
            if game.name.lower() == cleaned_name.lower():
                state.message = game.name + " was removed from your library."
                found_game = True
            else:
                remaining_games.append(game)

        state.games = remaining_games

        if not found_game:
            state.message = "That game was not found in your library."

    return library(state)


# The Preferences page asks what the user wants to play right now.
# These choices are separate from the details stored for each Game.
@route
def preferences(state: State) -> Page:
    return Page(state, [
        Header("Set Your Preferences"),
        "Choose what you feel like playing.",
        "Genre you want to play:",
        SelectBox("genre_choice", [
            "Any", "Action", "Adventure", "Puzzle", "RPG",
            "Racing", "Shooter", "Simulation", "Sports", "Strategy", "Other"
        ], state.selected_genre),
        "\n",
        "Which games should be included?",
        SelectBox("completion_choice", [
            "Any", "Completed", "Unfinished"
        ], state.completion_filter),
        "\n",
        Button("Save Preferences", "save_preferences")
    ])


# Stores the user's preference choices in their own State fields.
@route
def save_preferences(state: State, genre_choice: str,
                     completion_choice: str) -> Page:
    state.selected_genre = genre_choice
    state.completion_filter = completion_choice
    state.message = "Your preferences have been saved."
    return recommended_game(state)


# Checks the library against the saved preferences.
@route
def recommended_game(state: State) -> Page:
    matching_games = []

    for game in state.games:
        genre_matches = (
            state.selected_genre == "Any"
            or game.genre == state.selected_genre
        )

        completion_matches = (
            state.completion_filter == "Any"
            or (state.completion_filter == "Completed" and game.completed)
            or (state.completion_filter == "Unfinished" and not game.completed)
        )
    
        if genre_matches and completion_matches:
            matching_games.append(game)
    
    state.recommended_games = matching_games
    
    if len(state.recommended_games) == 0:
        state.message = (
            "No games match those preferences. "
            "Try changing your preferences or adding games."
        )
    else:
        state.message = str(len(state.recommended_games)) + " game(s) match your preferences."

    return view_recommendation(state)


# Displays every game that matches the saved preferences.
@route
def view_recommendation(state: State) -> Page:
    page_content = [
        Header("Your Recommendations"),
        state.message
    ]

    if not state.recommended_games:
        page_content.append("No games matched your preferences.")
        page_content.append("Try selecting Any for one or both preferences.")

    else:
        for game in state.recommended_games:
            if game.completed:
                status = "Completed"
            else:
                status = "Unfinished"

            page_content.append(
                game.name + " (" + game.genre + ", " + status + ")"
            )
            page_content.append(game.description)

    page_content.append(Button("Change Preferences", "preferences"))
    page_content.append(Button("View Library", "library"))
    page_content.append(Button("Home", "index"))

    return Page(state, page_content)
# assert_equal tests
test_state = State([], [], "Any", "Any", "")

save_game(test_state, "Minecraft", "Simulation", False, "Building game")

assert_equal(len(test_state.games), 1)
assert_equal(test_state.games[0].name, "Minecraft")
assert_equal(test_state.games[0].genre, "Simulation")
assert_equal(test_state.games[0].completed, False)

# Checks if to make sure no game is added if game is empty

test_state = State([], [], "Any", "Any", "")

save_game(test_state, "   ", "Action", False, "Test description")

assert_equal(len(test_state.games), 0)
assert_equal(test_state.message, "Please enter a game name. No game was added.")

# Starts the website with an empty library and default preferences.
start_server(State(
    games=[],
    recommended_games=[],
    selected_genre="Any",
    completion_filter="Any",
    message="Welcome to Game Selector! Add games to begin."
))
