import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import re

class ContainerManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão de Containers")
        self.root.geometry("1000x700")
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        # Inicializar banco de dados
        self.init_database()
        
        # Frame de login
        self.login_frame = ttk.Frame(root, padding="20")
        self.login_frame.pack(pady=50)
        
        # Título do login
        ttk.Label(self.login_frame, text="Sistema de Gestão de Containers", 
                 style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=20)
        
        # Variáveis de login
        self.razao_social_var = tk.StringVar()
        self.cnpj_var = tk.StringVar()
        self.senha_var = tk.StringVar()
        
        # Componentes de login
        ttk.Label(self.login_frame, text="Razão Social:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(self.login_frame, textvariable=self.razao_social_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.login_frame, text="CNPJ:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.cnpj_entry = ttk.Entry(self.login_frame, textvariable=self.cnpj_var, width=30)
        self.cnpj_entry.grid(row=2, column=1, padx=5, pady=5)
        self.cnpj_entry.bind('<KeyRelease>', self.format_cnpj)
        
        ttk.Label(self.login_frame, text="Senha:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(self.login_frame, textvariable=self.senha_var, show="*", width=30).grid(row=3, column=1, padx=5, pady=5)
        
        # Frame para botões de login
        button_frame = ttk.Frame(self.login_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Login", command=self.login, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cadastrar", command=self.cadastrar, width=15).pack(side=tk.LEFT, padx=5)
        
        # Frame principal (inicialmente oculto)
        self.main_frame = ttk.Frame(root, padding="10")
        
        # Notebook para as abas
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill='both')
        
        # Configurar abas
        self.containers_frame = ttk.Frame(self.notebook, padding="10")
        self.agendamentos_frame = ttk.Frame(self.notebook, padding="10")
        
        self.notebook.add(self.containers_frame, text='Gestão de Containers')
        self.notebook.add(self.agendamentos_frame, text='Agendamentos')
        
        self.setup_containers_tab()
        self.setup_agendamentos_tab()

    def init_database(self):
        conn = sqlite3.connect('container_system.db')
        c = conn.cursor()
        
        # Create tables with correct schema
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                    (razao_social TEXT, cnpj TEXT PRIMARY KEY, senha TEXT)''')
        
        # Updated container table schema with tipo_container
        c.execute('''CREATE TABLE IF NOT EXISTS containers
                    (id TEXT PRIMARY KEY,
                     tipo_container TEXT,
                     altura REAL,
                     largura REAL,
                     comprimento REAL,
                     status TEXT,
                     origem TEXT,
                     destino TEXT,
                     data_entrada TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS agendamentos
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     container_id TEXT,
                     data_agendamento TEXT,
                     tipo_operacao TEXT,
                     FOREIGN KEY(container_id) REFERENCES containers(id))''')
        
        conn.commit()
        conn.close()

    def setup_containers_tab(self):
        # Frame para entrada de dados
        input_frame = ttk.LabelFrame(self.containers_frame, text="Dados do Container", padding="10")
        input_frame.pack(fill="x", padx=5, pady=5)
        
        # Variáveis
        self.container_vars = {
            'ID do Container': tk.StringVar(),
            'Tipo de Container': tk.StringVar(),
            'Altura (m)': tk.StringVar(),
            'Largura (m)': tk.StringVar(),
            'Comprimento (m)': tk.StringVar(),
            'Status': tk.StringVar(),
            'Origem': tk.StringVar(),
            'Destino': tk.StringVar()
        }
        
        # Grid de entrada de dados
        row = 0
        for label, var in self.container_vars.items():
            ttk.Label(input_frame, text=label).grid(row=row, column=0, padx=5, pady=5, sticky='e')
            
            if label == 'Status':
                status_combo = ttk.Combobox(input_frame, textvariable=var, state='readonly')
                status_combo['values'] = ('Disponível', 'Em uso', 'Necessita manutenção')
                status_combo.grid(row=row, column=1, padx=5, pady=5, sticky='w')
            elif label == 'Tipo de Container':
                tipo_combo = ttk.Combobox(input_frame, textvariable=var, state='readonly')
                tipo_combo['values'] = ('Dry', 'Reefer', 'Open Top', 'Flat Rack', 'Tank')
                tipo_combo.grid(row=row, column=1, padx=5, pady=5, sticky='w')
            else:
                ttk.Entry(input_frame, textvariable=var).grid(row=row, column=1, padx=5, pady=5, sticky='w')
            
            row += 1
        
        # Frame para botões
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Adicionar Container", 
                  command=self.adicionar_container).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remover Container", 
                  command=self.remover_container).pack(side=tk.LEFT, padx=5)
        
        # Treeview para listar containers
        self.container_tree = ttk.Treeview(self.containers_frame, 
                                         columns=list(self.container_vars.keys()),
                                         show='headings')
        
        # Configurar colunas
        for col in self.container_vars.keys():
            self.container_tree.heading(col, text=col)
            self.container_tree.column(col, width=100)
        
        self.container_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(self.containers_frame, orient="vertical", 
                                command=self.container_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.container_tree.configure(yscrollcommand=scrollbar.set)

    def setup_agendamentos_tab(self):
        # Frame para entrada de dados
        input_frame = ttk.LabelFrame(self.agendamentos_frame, text="Novo Agendamento", padding="10")
        input_frame.pack(fill="x", padx=5, pady=5)
        
        # Variáveis
        self.container_id_var = tk.StringVar()
        self.data_agendamento_var = tk.StringVar()
        self.tipo_operacao_var = tk.StringVar()
        
        # Campos de entrada
        ttk.Label(input_frame, text="ID do Container:").grid(row=0, column=0, padx=5, pady=5)
        self.container_combo = ttk.Combobox(input_frame, textvariable=self.container_id_var, state='readonly')
        self.container_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Botão de atualizar lista de containers
        ttk.Button(input_frame, text="↻", width=3, 
                  command=self.atualizar_lista_containers).grid(row=0, column=2, padx=2, pady=5)
        
        ttk.Label(input_frame, text="Data (DD/MM/AAAA):").grid(row=1, column=0, padx=5, pady=5)
        self.data_entry = ttk.Entry(input_frame, textvariable=self.data_agendamento_var)
        self.data_entry.grid(row=1, column=1, padx=5, pady=5)
        self.data_entry.bind('<KeyRelease>', self.format_data)
        
        ttk.Label(input_frame, text="Tipo de Operação:").grid(row=2, column=0, padx=5, pady=5)
        operacao_combo = ttk.Combobox(input_frame, textvariable=self.tipo_operacao_var, state='readonly')
        operacao_combo['values'] = ('Carregamento', 'Descarregamento', 'Manutenção')
        operacao_combo.grid(row=2, column=1, padx=5, pady=5)
        
        # Frame para botões
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Criar Agendamento", 
                  command=self.criar_agendamento).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remover Agendamento", 
                  command=self.remover_agendamento).pack(side=tk.LEFT, padx=5)
        
        # Treeview para listar agendamentos
        self.agendamento_tree = ttk.Treeview(self.agendamentos_frame,
                                           columns=('ID', 'Container ID', 'Data', 'Operação'),
                                           show='headings')
        
        for col in ('ID', 'Container ID', 'Data', 'Operação'):
            self.agendamento_tree.heading(col, text=col)
            self.agendamento_tree.column(col, width=150)
        
        self.agendamento_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(self.agendamentos_frame, orient="vertical", 
                                command=self.agendamento_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.agendamento_tree.configure(yscrollcommand=scrollbar.set)
        
        # Carregar lista inicial de containers
        self.atualizar_lista_containers()

    def format_cnpj(self, event):
        # Get only digits from the input
        cnpj = ''.join(filter(str.isdigit, self.cnpj_var.get()))
        
        # Limit to 14 digits
        cnpj = cnpj[:14]
        
        # Format the CNPJ
        if len(cnpj) <= 2:
            formatted = cnpj
        elif len(cnpj) <= 5:
            formatted = f"{cnpj[:2]}.{cnpj[2:]}"
        elif len(cnpj) <= 8:
            formatted = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:]}"
        elif len(cnpj) <= 12:
            formatted = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:]}"
        else:
            formatted = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        
        # Update the entry
        self.cnpj_var.set(formatted)
        
        # Move cursor to end
        self.cnpj_entry.icursor(len(formatted))

    def format_data(self, event):
        # Get only digits from the input
        data = ''.join(filter(str.isdigit, self.data_agendamento_var.get()))
        
        # Limit to 8 digits
        data = data[:8]
        
        # Format the date
        formatted = ''
        for i, char in enumerate(data):
            if i == 2 or i == 4:
                formatted += '/' + char
            else:
                formatted += char
        
        # Update the entry
        self.data_agendamento_var.set(formatted)
        
        # Move cursor to end
        self.data_entry.icursor(len(formatted))

    def validar_data(self, data_str):
        try:
            return datetime.strptime(data_str, '%d/%m/%Y')
        except ValueError:
            return None

    def carregar_containers(self):
        # Limpar treeview
        for item in self.container_tree.get_children():
            self.container_tree.delete(item)
            
        # Carregar dados do banco
        conn = sqlite3.connect('container_system.db')
        c = conn.cursor()
        
        c.execute("SELECT * FROM containers")
        containers = c.fetchall()
        
        for container in containers:
            self.container_tree.insert('', 'end', values=container)
            
        conn.close()

    def carregar_agendamentos(self):
        # Limpar treeview
        for item in self.agendamento_tree.get_children():
            self.agendamento_tree.delete(item)
            
        # Carregar dados do banco
        conn = sqlite3.connect('container_system.db')
        c = conn.cursor()
        
        c.execute("SELECT * FROM agendamentos")
        agendamentos = c.fetchall()
        for agendamento in agendamentos:
            self.agendamento_tree.insert('', 'end', values=agendamento)
            
        conn.close()

    def atualizar_lista_containers(self):
        """Atualiza a lista de containers disponíveis no combobox"""
        conn = sqlite3.connect('container_system.db')
        c = conn.cursor()
        
        try:
            # Buscar todos os IDs de containers cadastrados
            c.execute("SELECT id FROM containers")
            containers = c.fetchall()
            
            # Atualizar valores do combobox
            self.container_combo['values'] = [container[0] for container in containers]
            
            # Se não houver containers, limpar a seleção atual
            if not containers:
                self.container_combo.set('')
                self.container_id_var.set('')
            
        finally:
            conn.close()

    def login(self):
        """Verifica credenciais e faz login no sistema"""
        razao_social = self.razao_social_var.get().strip()
        cnpj = self.cnpj_var.get().strip()
        senha = self.senha_var.get().strip()
        
        if not all([razao_social, cnpj, senha]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios")
            return
        
        conn = sqlite3.connect('container_system.db')
        c = conn.cursor()
        
        try:
            c.execute("SELECT * FROM usuarios WHERE cnpj=? AND senha=?", (cnpj, senha))
            user = c.fetchone()
            
            if user:
                self.login_frame.pack_forget()
                self.main_frame.pack(expand=True, fill='both')
                self.carregar_containers()
                self.carregar_agendamentos()
            else:
                messagebox.showerror("Erro", "Credenciais inválidas")
        finally:
            conn.close()

    def cadastrar(self):
        """Cadastra novo usuário no sistema"""
        razao_social = self.razao_social_var.get().strip()
        cnpj = self.cnpj_var.get().strip()
        senha = self.senha_var.get().strip()
        
        if not all([razao_social, cnpj, senha]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios")
            return
            
        # Validar formato do CNPJ
        cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
        if len(cnpj_limpo) != 14:
            messagebox.showerror("Erro", "CNPJ inválido")
            return
        
        conn = sqlite3.connect('container_system.db')
        c = conn.cursor()
        
        try:
            # Verificar se CNPJ já existe
            c.execute("SELECT * FROM usuarios WHERE cnpj=?", (cnpj,))
            if c.fetchone():
                messagebox.showerror("Erro", "CNPJ já cadastrado")
                return
            
            # Inserir novo usuário
            c.execute("INSERT INTO usuarios VALUES (?, ?, ?)", 
                     (razao_social, cnpj, senha))
            conn.commit()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso")
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {str(e)}")
        finally:
            conn.close()

    def adicionar_container(self):
        """Adiciona novo container ao sistema"""
        # Validar campos
        valores = {k: v.get().strip() for k, v in self.container_vars.items()}
        
        if not all(valores.values()):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios")
            return
            
        try:
            # Validar dimensões
            for dim in ['Altura (m)', 'Largura (m)', 'Comprimento (m)']:
                float(valores[dim])
        except ValueError:
            messagebox.showerror("Erro", "Dimensões devem ser números válidos")
            return
        
        conn = sqlite3.connect('container_system.db')
        c = conn.cursor()
        
        try:
            # Verificar se ID já existe
            c.execute("SELECT id FROM containers WHERE id=?", (valores['ID do Container'],))
            if c.fetchone():
                messagebox.showerror("Erro", "Container ID já existe")
                return
            
            # Inserir container
            c.execute("""INSERT INTO containers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (valores['ID do Container'], valores['Tipo de Container'],
                      float(valores['Altura (m)']), float(valores['Largura (m)']),
                      float(valores['Comprimento (m)']), valores['Status'],
                      valores['Origem'], valores['Destino'],
                      datetime.now().strftime('%d/%m/%Y')))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Container adicionado com sucesso")
            
            # Atualizar visualizações
            self.carregar_containers()
            self.atualizar_lista_containers()
            
            # Limpar campos
            for var in self.container_vars.values():
                var.set('')
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao adicionar container: {str(e)}")
        finally:
            conn.close()

    def remover_container(self):
        """Remove container selecionado"""
        selection = self.container_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um container para remover")
            return
            
        if not messagebox.askyesno("Confirmar", "Deseja realmente remover o container?"):
            return
            
        container_id = self.container_tree.item(selection[0])['values'][0]
        
        conn = sqlite3.connect('container_system.db')
        c = conn.cursor()
        
        try:
            # Verificar se há agendamentos
            c.execute("SELECT * FROM agendamentos WHERE container_id=?", (container_id,))
            if c.fetchone():
                if not messagebox.askyesno("Aviso", 
                    "Existem agendamentos para este container. Deseja removê-los também?"):
                    return
                
                # Remover agendamentos
                c.execute("DELETE FROM agendamentos WHERE container_id=?", (container_id,))
            
            # Remover container
            c.execute("DELETE FROM containers WHERE id=?", (container_id,))
            conn.commit()
            
            # Atualizar visualizações
            self.carregar_containers()
            self.carregar_agendamentos()
            self.atualizar_lista_containers()
            
            messagebox.showinfo("Sucesso", "Container removido com sucesso")
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao remover container: {str(e)}")
        finally:
            conn.close()

    def criar_agendamento(self):
        """Cria novo agendamento"""
        container_id = self.container_id_var.get().strip()
        data = self.data_agendamento_var.get().strip()
        operacao = self.tipo_operacao_var.get().strip()
        
        if not all([container_id, data, operacao]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios")
            return
            
        # Validar data
        data_obj = self.validar_data(data)
        if not data_obj:
            messagebox.showerror("Erro", "Data inválida")
            return
            
        if data_obj.date() < datetime.now().date():
            messagebox.showerror("Erro", "Data não pode ser no passado")
            return
        
        conn = sqlite3.connect('container_system.db')
        c = conn.cursor()
        
        try:
            # Verificar se container existe
            c.execute("SELECT * FROM containers WHERE id=?", (container_id,))
            if not c.fetchone():
                messagebox.showerror("Erro", "Container não encontrado")
                return
            
            # Verificar conflitos de agendamento
            c.execute("""SELECT * FROM agendamentos 
                        WHERE container_id=? AND data_agendamento=?""",
                     (container_id, data))
            
            if c.fetchone():
                messagebox.showerror("Erro", "Já existe um agendamento para este container nesta data")
                return
            
            # Criar agendamento
            c.execute("""INSERT INTO agendamentos (container_id, data_agendamento, tipo_operacao)
                        VALUES (?, ?, ?)""", (container_id, data, operacao))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Agendamento criado com sucesso")
            
            # Atualizar visualização e limpar campos
            self.carregar_agendamentos()
            self.container_id_var.set('')
            self.data_agendamento_var.set('')
            self.tipo_operacao_var.set('')
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao criar agendamento: {str(e)}")
        finally:
            conn.close()

    def remover_agendamento(self):
        """Remove agendamento selecionado"""
        selection = self.agendamento_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um agendamento para remover")
            return
            
        if not messagebox.askyesno("Confirmar", "Deseja realmente remover o agendamento?"):
            return
            
        agendamento_id = self.agendamento_tree.item(selection[0])['values'][0]
        
        conn = sqlite3.connect('container_system.db')
        c = conn.cursor()
        
        try:
            c.execute("DELETE FROM agendamentos WHERE id=?", (agendamento_id,))
            conn.commit()
            
            self.carregar_agendamentos()
            messagebox.showinfo("Sucesso", "Agendamento removido com sucesso")
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao remover agendamento: {str(e)}")
        finally:
            conn.close()

if __name__ == '__main__':
    root = tk.Tk()
    app = ContainerManagementSystem(root)
    root.mainloop()