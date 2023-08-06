from customtkinter import CTkFrame, CTkScrollableFrame, CTkLabel


class CTkList(CTkScrollableFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

    def add(self, text="", text_anchor="w"):
        __frame = CTkFrame(self)
        __label = CTkLabel(__frame, text=text, anchor=text_anchor)
        __label.pack(fill="x", padx=5, pady=5, ipadx=2.5, ipady=2.5)
        __frame.pack(fill="x", padx=2.5, pady=2.5)

        def click(event):
            self.event_generate("<<ListSelected>>", x=event.x, y=event.y, state=event.state, data={"text": text})

        __frame.bind("<Button-1>", click)
        __label.bind("<Button-1>", click)

        return __frame, __label

    def clear(self):
        for index in self.winfo_children(): index.destroy()


if __name__ == '__main__':
    from customtkinterx import CTkCustom

    root = CTkCustom()
    root.create_sizegrip()

    list = CTkList(root.mainframe)

    for index in range(20):
        list.add("list"+str(index+1))

    list.bind("<<ListSelected>>", lambda event: print(event))

    list.pack(fill="both", expand="yes", padx=5, pady=5)

    root.mainloop()