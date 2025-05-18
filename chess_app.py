import streamlit as st
import chess
import chess.svg
import random
import streamlit.components.v1 as components

st.set_page_config(page_title="Chess Game", page_icon="♟️", layout="wide")

st.title("♟️ Streamlit Chess Game")

st.markdown("""
<style>
.move-table td {
    padding: 0.2em 0.5em;
    font-size: 1.1em;
}
</style>
""", unsafe_allow_html=True)

# --- Game State ---
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
    st.session_state.move_history = []
    st.session_state.play_mode = "Human vs Random AI"
    st.session_state.status = ""

def reset_game():
    st.session_state.board = chess.Board()
    st.session_state.move_history = []
    st.session_state.status = ""

# --- Sidebar for Mode Selection ---
st.sidebar.header("Settings")
mode = st.sidebar.radio("Play mode", ["Human vs Random AI", "Human vs Human"], key="mode")
if mode != st.session_state.play_mode:
    st.session_state.play_mode = mode
    reset_game()

if st.sidebar.button("Reset Game"):
    reset_game()

# --- Chessboard Display ---
board_svg = chess.svg.board(st.session_state.board, size=400, lastmove=st.session_state.board.peek() if st.session_state.board.move_stack else None)
components.html(board_svg, height=420, width=420)

# --- Move Input ---
if not st.session_state.board.is_game_over():
    st.write(f"**Turn:** {'White' if st.session_state.board.turn else 'Black'}")
    move_uci = st.text_input("Enter your move (e.g., e2e4)", key="move_input")
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Make Move"):
            try:
                move = chess.Move.from_uci(move_uci.strip())
                if move in st.session_state.board.legal_moves:
                    st.session_state.board.push(move)
                    st.session_state.move_history.append(move_uci)
                    st.session_state.status = ""
                    # If vs AI and it's AI's turn
                    if st.session_state.play_mode == "Human vs Random AI" and not st.session_state.board.is_game_over() and not st.session_state.board.turn:
                        legal_moves = list(st.session_state.board.legal_moves)
                        ai_move = random.choice(legal_moves)
                        st.session_state.board.push(ai_move)
                        st.session_state.move_history.append(ai_move.uci())
                else:
                    st.session_state.status = "Illegal move!"
            except Exception as e:
                st.session_state.status = f"Invalid move format! ({e})"
    with col2:
        if st.button("Undo Move"):
            if len(st.session_state.board.move_stack) > 0:
                st.session_state.board.pop()
                st.session_state.move_history.pop()
                if st.session_state.play_mode == "Human vs Random AI" and len(st.session_state.board.move_stack) > 0 and not st.session_state.board.turn:
                    st.session_state.board.pop()
                    st.session_state.move_history.pop()
else:
    result = st.session_state.board.result()
    if result == "1-0":
        st.success("White wins! 🎉")
    elif result == "0-1":
        st.success("Black wins! 🎉")
    else:
        st.info("Draw game.")

if st.session_state.status:
    st.warning(st.session_state.status)

# --- Show Move History ---
st.markdown("### Move History")
move_pairs = [st.session_state.move_history[i:i+2] for i in range(0, len(st.session_state.move_history), 2)]
move_table = "<table class='move-table'><tr><th>#</th><th>White</th><th>Black</th></tr>"
for idx, pair in enumerate(move_pairs):
    move_table += f"<tr><td>{idx+1}</td><td>{pair[0] if len(pair)>0 else ''}</td><td>{pair[1] if len(pair)>1 else ''}</td></tr>"
move_table += "</table>"
st.markdown(move_table, unsafe_allow_html=True)

# --- Show FEN for debugging ---
with st.expander("Show FEN (for debugging or saving):"):
    st.code(st.session_state.board.fen())
