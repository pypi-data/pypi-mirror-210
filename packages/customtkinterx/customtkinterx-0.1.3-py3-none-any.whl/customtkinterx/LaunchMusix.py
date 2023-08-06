from tkinter import *
from tkinter import ttk
from customtkinter import *
from customtkinterx import *

def run():
    from sys import platform

    CTkFluentTheme()

    set_appearance_mode("system")

    tk_root = CTkCustom()
    tk_root.create_sizegrip()
    tk_root.wm_geometry(f"350x620")

    tk_root.title("Musix.Py")
    tk_root.titlebar_title.configure(text="Musix.Py")

    frame_search = CTkFrame(tk_root.mainframe)
    combobox_search = CTkComboBox(frame_search, values=["Cloud Music"])
    combobox_search.set("Cloud Music")
    combobox_search.pack(fill="x", side="top", padx=5, pady=5)
    var_search = StringVar(value="Hopes And Dreams")
    entry_search = CTkEntry(frame_search, textvariable=var_search)
    entry_search.pack(side="left", fill="x", expand=True, padx=(5, 2.5), pady=5)
    switch_search = CTkSwitch(frame_search, text="Download", width=60)
    switch_search.pack(side="right", padx=(2.5, 5), pady=5)
    button_search = CTkButton(frame_search, text="Search", width=60)
    button_search.pack(side="right", padx=(2.5, 5), pady=5)
    frame_search.pack(fill="x", side="top", padx=5, pady=(5, 2.5))

    frame_results = CTkScrollableFrame(tk_root.mainframe)
    frame_results.pack(fill="both", expand="yes", padx=5, pady=(2.5, 5))


    def cloud_search():
        def _search():
            from cloudmusic import search, getMusic
            results = search(entry_search.get(), 15)
            for index in results:
                print(index.name)
                __ = index

                __frame = CTkFrame(frame_results)
                __frame.setvar()
                __frame.pack(fill="x", padx=2.5, pady=2.5, ipadx=5, ipady=5)
                CTkLabel(__frame, text=index.name).pack(side="left", fill="x", padx=5, pady=2.5)
                CTkLabel(__frame, text=index.id).pack(side="right", padx=5, pady=2.5)
                CTkLabel(__frame, text=','.join(index.artist)).pack(side="right", padx=5, pady=2.5)

                if switch_search.get():
                    __.download()

        from threading import Thread
        _search()


    def search():
        for index in frame_results.winfo_children(): index.destroy()
        if combobox_search.get() == "Cloud Music": cloud_search()


    button_search.configure(command=search)

    tk_root.mainloop()


if __name__ == '__main__':
    run()