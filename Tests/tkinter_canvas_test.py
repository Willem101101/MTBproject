import tkinter as tk

root = tk.Tk()
root.configure(width=500, height= 350)

c = tk.Canvas(root, bg="red")
c.create_text(30, 60, text="text1", font="Trebuchet 15")
c.create_rectangle(200, 50, 10, 10, fill="black")
c.place(width= 400, height=250, x=50, y=50)
root.mainloop()
