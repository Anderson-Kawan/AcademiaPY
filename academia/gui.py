from tkinter import *
from tkinter import messagebox
from ficha import formatar_ficha
from database import buscar_aluno_nome_ou_matricula, buscar_ficha
from printer import imprimir_ficha
from utils import limpar_texto
from PIL import Image, ImageTk

# Módulo gui.py

def processar_pesquisa(event=None):
    busca = entry_busca.get().strip()
    if not busca:
        messagebox.showwarning("Aviso", "Por favor, digite o nome ou matrícula do aluno.")
        return

    # Limpar os botões e campos de texto anteriores
    text_area.delete(1.0, "end")
    for widget in buttons_canvas.winfo_children():
        widget.destroy()
    for widget in text_buttons_frame.winfo_children():
        widget.destroy()

    # Verificar se a busca é uma matrícula (número)
    if busca.isdigit():
        processar(int(busca))
    else:
        resultado = buscar_aluno_nome_ou_matricula(busca)

        # Verificar se o resultado é uma string (erro ou mensagem)
        if isinstance(resultado, str):
            messagebox.showerror("Erro", resultado)
            return

        # Verificar se o resultado é um dicionário (único aluno)
        if isinstance(resultado, dict):
            resultado = [resultado]  # Converter o dicionário em uma lista com um único aluno

        # Verificar se o resultado é uma lista de alunos
        if not isinstance(resultado, list):
            messagebox.showerror("Erro", f"Formato de retorno inválido: {type(resultado)}")
            return

        if not resultado:  # Se a lista estiver vazia
            messagebox.showinfo("Informação", "Nenhum aluno encontrado.")
            return

        # Criar um Frame dentro do Canvas para conter os botões
        button_frame = Frame(buttons_canvas)
        buttons_canvas.create_window((0, 0), window=button_frame, anchor="nw")

        # Exibir os alunos encontrados com botões
        for aluno in resultado:  # Iterar sobre a lista de alunos
            nome_aluno = f"{aluno['nome']} {aluno.get('sobrenome', '')}".strip()
            matricula_aluno = aluno["id"]

            # Criar um botão para cada aluno encontrado
            Button(
                button_frame,
                text=nome_aluno,
                command=lambda matricula=matricula_aluno: processar(matricula)
            ).pack(pady=5, anchor="w")

        # Atualizar a área rolável do Canvas
        button_frame.update_idletasks()
        buttons_canvas.config(scrollregion=buttons_canvas.bbox("all"))

def exibir_ficha(conteudo_ficha, nome_ficha):
    # Limpar o text_area
    text_area.delete(1.0, "end")
    text_area.insert("end", conteudo_ficha)

    # Limpar o frame de botões de impressão
    for widget in text_buttons_frame.winfo_children():
        widget.destroy()

    # Adicionar botão de imprimir
    Button(
        text_buttons_frame,
        text=f"Imprimir Ficha: {nome_ficha}",
        command=lambda ficha=conteudo_ficha, nome_ficha=nome_ficha: imprimir_ficha(ficha, nome_ficha)
    ).pack(pady=10, anchor="w")

def processar(codigo):
    # Limpar o text_area e os botões anteriores
    text_area.delete(1.0, "end")
    for widget in buttons_canvas.winfo_children():
        widget.destroy()
    for widget in text_buttons_frame.winfo_children():
        widget.destroy()

    # Buscar as fichas do aluno
    fichas = buscar_ficha(codigo)

    if isinstance(fichas, str):  # Se retornar uma string, é um erro
        messagebox.showerror("Erro", fichas)
        return

    if isinstance(fichas, dict):  # Se retornar um dicionário (única ficha)
        fichas = [fichas]  # Converter em uma lista com um único item

    if isinstance(fichas, list):
        # Criar um Frame dentro do Canvas para conter os botões
        button_list_frame = Frame(buttons_canvas)
        buttons_canvas.create_window((0, 0), window=button_list_frame, anchor="nw")

        # Exibir cada ficha como um botão
        for i, ficha in enumerate(fichas):
            nome_ficha = ficha.get("treino_nome", "Ficha sem nome")
            conteudo_ficha = formatar_ficha(ficha)  # Usar a função formatar_ficha

            # Criar um botão para cada ficha
            Button(
                button_list_frame,
                text=f"Ficha {i + 1}: {nome_ficha}",
                command=lambda ficha=conteudo_ficha, nome_ficha=nome_ficha: exibir_ficha(ficha, nome_ficha)
            ).pack(pady=5, anchor="w")

        # Atualizar a área rolável do Canvas
        button_list_frame.update_idletasks()
        buttons_canvas.config(scrollregion=buttons_canvas.bbox("all"))
    else:
        text_area.insert("end", fichas)

# Interface gráfica
app = Tk()
app.title("Busca e Impressão de Fichas")

# Carregar e exibir logo
# logo_path = "c:/Users/PC- CORDENACAO -03/Desktop/sistema_academia/Logo.jpeg"
# logo = Image.open(logo_path)
# logo = logo.resize((300, 100), Image.Resampling.LANCZOS)
# logo_img = ImageTk.PhotoImage(logo)

# logo_label = Label(app, image=logo_img)
# logo_label.pack(side=TOP, pady=10)

Label(app, text="Buscar por Nome ou Matrícula:").pack(pady=5)
entry_busca = Entry(app, width=30)
entry_busca.pack(pady=5)

# Vincular o evento de pressionar "Enter" à função processar_pesquisa
entry_busca.bind("<Return>", processar_pesquisa)

Button(app, text="Buscar", command=processar_pesquisa).pack(pady=5)

frame_principal = Frame(app)
frame_principal.pack(padx=10, pady=10, fill=BOTH, expand=True)

frame_texto = Frame(frame_principal)
frame_texto.pack(side=LEFT, fill=BOTH, expand=True)

text_area = Text(frame_texto, height=20, width=60, wrap="word", state="normal")
text_area.pack(side=LEFT, fill=BOTH, expand=True)

scrollbar = Scrollbar(frame_texto, orient=VERTICAL, command=text_area.yview)
scrollbar.pack(side=RIGHT, fill=Y)

text_area.config(yscrollcommand=scrollbar.set)

# Canvas para rolagem dos botões
buttons_canvas_frame = Frame(frame_principal)
buttons_canvas_frame.pack(side=LEFT, fill=BOTH, expand=1)

buttons_canvas = Canvas(buttons_canvas_frame)
buttons_canvas.pack(side=LEFT, fill=BOTH, expand=1)

buttons_scrollbar = Scrollbar(buttons_canvas_frame, orient=VERTICAL, command=buttons_canvas.yview)
buttons_scrollbar.pack(side=RIGHT, fill=Y)

buttons_canvas.config(yscrollcommand=buttons_scrollbar.set)

text_buttons_frame = Frame(frame_principal)
text_buttons_frame.pack(side=RIGHT, fill=Y)

app.mainloop()