# import pdb
# import pandas as pd
# from plotly import express as px
#
# def display_results(log):
#     df_commod = log['commod']
#     df_commod['ts'] = log['clock']['ts']
#     df_commod = pd.melt(df_commod, id_vars=['ts'], value_vars=[col for col in df_commod.columns if col != 'ts'])
#     fig_commod = px.line(df_commod, x='ts', y='value', color='series')
#
#     df_actions = log['actions']
#     df_actions['ts'] = log['clock']['ts']
#     df_actions = pd.melt(df_actions, id_vars=['ts'], value_vars=[col for col in df_actions.columns if col != 'ts'])
#     fig_actions = px.bar(df_actions, x='ts', y='value', color='series')
#
#     fig_commod.show()
#     fig_actions.show()
#

import tkinter as tk
import tkinter.ttk as ttk


def event_button(event: tk.Event):
    print("YOOOOOO")


if __name__ == "__main__":
    # Base window
    window = tk.Tk()
    window.title("Hello world")
    window.geometry("400x600+500+50")
    # Button
    btn = tk.Button(window, text="Go!", fg='blue', font=("Calibri Light", 10))
    btn.place(x=100, y=100)
    # Label
    lbl = tk.Label(window, text="That's a label!", fg='red', font=("Calibri Light", 10))
    lbl.place(x=100, y=150)
    # Entry
    entry_field = tk.Entry(window, text="That's a field to fill")
    entry_field.place(x=100, y=200)
    # Combobox
    combobox = ttk.Combobox(window, values=("one", "two", "three"))
    combobox.place(x=100, y=250)
    # Listbox
    listbox = tk.Listbox(window, height=5, selectmode="multiple")
    for num in ["one", "two", "three"]:
        listbox.insert(tk.END, num)
    listbox.place(x=100, y=300)
    # Radio button
    v0 = tk.IntVar()
    rad_btn_male = tk.Radiobutton(window, text="male", variable=v0, value=1)
    rad_btn_female = tk.Radiobutton(window, text="female", variable=v0, value=2)
    rad_btn_male.place(x=0, y=320)
    rad_btn_female.place(x=0, y=340)
    # Check button
    v1 = tk.IntVar()
    check_btn = tk.Checkbutton(window, text="I'm in!", variable=v1)
    check_btn.place(x=0, y=400)
    btn.bind("<Button-1>", event_button)
    # Events
    window.mainloop()
