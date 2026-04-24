import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
from algorithms import bfs, dfs

class DroneDeliveryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Delivery Path Finder - Professional Visualization")
        self.root.geometry("1300x850")
        self.root.configure(bg="#2c3e50")

        # Configuration
        self.grid_size = 20
        self.cell_size = 30
        self.start_pos = (0, 0)
        self.goal_pos = (19, 19)
        self.grid_data = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.rects = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Results Storage
        self.last_bfs_res = None
        self.last_dfs_res = None
        
        # UI State
        self.animation_speed = tk.DoubleVar(value=0.01)
        self.allow_diagonal = tk.BooleanVar(value=False)
        self.is_running = False

        self._setup_styles()
        self._create_widgets()
        self._draw_grid()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#2c3e50")
        style.configure("TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("SubHeader.TLabel", font=("Segoe UI", 12, "bold"), foreground="#3498db")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=5)
        
        # Treeview styling for comparison table
        style.configure("Treeview", background="#34495e", foreground="white", fieldbackground="#34495e", font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _create_widgets(self):
        # 1. SIDEBAR (CONTROLS)
        sidebar = ttk.Frame(self.root, padding="15")
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(sidebar, text="SKYROUTE AI", style="Header.TLabel").pack(pady=(0, 20))

        # Control Buttons
        btn_frame = ttk.Frame(sidebar)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Run BFS", command=self.run_bfs).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Run DFS", command=self.run_dfs).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Compare Both", command=self.run_comparison).pack(fill=tk.X, pady=10)
        
        ttk.Separator(sidebar, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Load Sample Grid", command=self.load_sample_grid).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Generate Random", command=self.generate_random_grid).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Reset Path", command=self.reset_path).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Clear Grid", command=self.clear_grid).pack(fill=tk.X, pady=2)

        # Options
        ttk.Label(sidebar, text="Settings", style="SubHeader.TLabel").pack(anchor=tk.W, pady=(20, 5))
        ttk.Checkbutton(sidebar, text="Allow Diagonal", variable=self.allow_diagonal).pack(anchor=tk.W)
        
        ttk.Label(sidebar, text="Animation Speed:").pack(anchor=tk.W, pady=(15,0))
        ttk.Scale(sidebar, from_=0.1, to=0.001, variable=self.animation_speed).pack(fill=tk.X)

        # Live Metrics
        ttk.Label(sidebar, text="Live Metrics", style="SubHeader.TLabel").pack(anchor=tk.W, pady=(30, 5))
        self.live_nodes_var = tk.StringVar(value="Nodes Explored: 0")
        tk.Label(sidebar, textvariable=self.live_nodes_var, bg="#2c3e50", fg="#f1c40f", font=("Consolas", 10)).pack(anchor=tk.W)
        self.curr_node_var = tk.StringVar(value="Current: None")
        tk.Label(sidebar, textvariable=self.curr_node_var, bg="#2c3e50", fg="#ecf0f1", font=("Consolas", 9)).pack(anchor=tk.W)

        # Legend
        legend_frame = ttk.Frame(sidebar)
        legend_frame.pack(fill=tk.X, pady=20)
        legends = [("green", "Start"), ("red", "Goal"), ("black", "Obstacle"), ("#f39c12", "Explored"), ("blue", "Final Path")]
        for color, text in legends:
            f = tk.Frame(legend_frame, bg="#2c3e50")
            f.pack(fill=tk.X)
            tk.Label(f, bg=color, width=2).pack(side=tk.LEFT, padx=5, pady=1)
            tk.Label(f, text=text, bg="#2c3e50", fg="#ecf0f1", font=("Segoe UI", 9)).pack(side=tk.LEFT)

        # 2. MAIN AREA (GRID & RESULTS)
        main_content = ttk.Frame(self.root, padding="10")
        main_content.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Canvas for Grid
        self.canvas = tk.Canvas(main_content, bg="#34495e", highlightthickness=0, bd=0)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_click)

        # 3. RESULTS & COMPARISON PANEL (RIGHT)
        results_panel = ttk.Frame(self.root, padding="15")
        results_panel.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(results_panel, text="ANALYSIS PANEL", style="Header.TLabel").pack(pady=(0, 10))

        # Comparison Table
        ttk.Label(results_panel, text="Side-by-Side Comparison", style="SubHeader.TLabel").pack(anchor=tk.W, pady=5)
        self.tree = ttk.Treeview(results_panel, columns=("Metric", "BFS", "DFS"), show='headings', height=4)
        self.tree.heading("Metric", text="Metric")
        self.tree.heading("BFS", text="BFS")
        self.tree.heading("DFS", text="DFS")
        self.tree.column("Metric", width=120)
        self.tree.column("BFS", width=80)
        self.tree.column("DFS", width=80)
        self.tree.pack(fill=tk.X, pady=5)
        
        # Initialize table rows
        self.tree.insert("", tk.END, values=("Path Length", "-", "-"), tags=("row1",))
        self.tree.insert("", tk.END, values=("Nodes Explored", "-", "-"), tags=("row2",))
        self.tree.insert("", tk.END, values=("Time (ms)", "-", "-"), tags=("row3",))
        
        # Conclusion Label
        self.conclusion_var = tk.StringVar(value="")
        tk.Label(results_panel, textvariable=self.conclusion_var, bg="#2c3e50", fg="#2ecc71", 
                 wraplength=280, font=("Segoe UI", 10, "italic")).pack(fill=tk.X, pady=10)

        # Detailed Path Log
        ttk.Label(results_panel, text="Detailed Path Trace", style="SubHeader.TLabel").pack(anchor=tk.W, pady=(10, 5))
        self.path_log = tk.Text(results_panel, width=40, height=20, bg="#1a252f", fg="#ecf0f1", 
                               font=("Consolas", 9), padx=5, pady=5, state=tk.DISABLED)
        self.path_log.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(results_panel, text="Note: DFS does not guarantee shortest path", font=("Segoe UI", 8, "italic"), foreground="#bdc3c7").pack(pady=5)

    def _draw_grid(self):
        self.canvas.delete("all")
        self.rects = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        offset = 5
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                color = "white"
                if (r, c) == self.start_pos: color = "green"
                elif (r, c) == self.goal_pos: color = "red"
                elif self.grid_data[r][c] == 1: color = "black"
                
                x1, y1 = c * self.cell_size + offset, r * self.cell_size + offset
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                self.rects[r][c] = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#7f8c8d")
        
        self.canvas.config(width=self.grid_size*self.cell_size + 10, height=self.grid_size*self.cell_size + 10)

    def _on_canvas_click(self, event):
        if self.is_running: return
        c = (event.x - 5) // self.cell_size
        r = (event.y - 5) // self.cell_size
        if 0 <= r < self.grid_size and 0 <= c < self.grid_size:
            if (r, c) == self.start_pos or (r, c) == self.goal_pos: return
            self.grid_data[r][c] = 1 if self.grid_data[r][c] == 0 else 0
            color = "black" if self.grid_data[r][c] == 1 else "white"
            self.canvas.itemconfig(self.rects[r][c], fill=color)

    def load_sample_grid(self):
        self.clear_grid()
        sample = [
            [0, 0, 0, 1, 0],
            [1, 1, 0, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0]
        ]
        self.grid_size = 5
        self.cell_size = 80 # Make it larger for the sample
        self.grid_data = sample
        self.start_pos = (0, 0)
        self.goal_pos = (4, 4)
        self._draw_grid()

    def generate_random_grid(self):
        # Reset to default size if it was changed by sample
        if self.grid_size != 20:
            self.grid_size = 20
            self.cell_size = 30
            self.grid_data = [[0 for _ in range(20)] for _ in range(20)]
            
        self.reset_path()
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if (r, c) == self.start_pos or (r, c) == self.goal_pos:
                    self.grid_data[r][c] = 0
                    continue
                self.grid_data[r][c] = 1 if random.random() < 0.25 else 0
        self._draw_grid()

    def clear_grid(self):
        self.grid_data = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self._draw_grid()
        self.reset_path()

    def reset_path(self):
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                color = "white"
                if (r, c) == self.start_pos: color = "green"
                elif (r, c) == self.goal_pos: color = "red"
                elif self.grid_data[r][c] == 1: color = "black"
                self.canvas.itemconfig(self.rects[r][c], fill=color)
        self.live_nodes_var.set("Nodes Explored: 0")
        self.curr_node_var.set("Current: None")
        self.conclusion_var.set("")

    def log_result(self, algo_name, res):
        self.path_log.config(state=tk.NORMAL)
        self.path_log.insert(tk.END, f"\n--- {algo_name} RESULT ---\n")
        if res["found"]:
            path_str = " → ".join([f"({r},{c})" for r, c in res["path"]])
            self.path_log.insert(tk.END, f"Path: {path_str}\n")
            self.path_log.insert(tk.END, f"Length: {res['path_length']}\n")
            self.path_log.insert(tk.END, f"Explored: {res['nodes_explored']}\n")
            self.path_log.insert(tk.END, f"Time: {res['elapsed_time']*1000:.2f} ms\n")
        else:
            self.path_log.insert(tk.END, "NO PATH FOUND\n")
        self.path_log.see(tk.END)
        self.path_log.config(state=tk.DISABLED)

    def update_table(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        b = self.last_bfs_res
        d = self.last_dfs_res
        
        self.tree.insert("", tk.END, values=("Path Length", 
                                            b["path_length"] if b else "-", 
                                            d["path_length"] if d else "-"))
        self.tree.insert("", tk.END, values=("Nodes Explored", 
                                            b["nodes_explored"] if b else "-", 
                                            d["nodes_explored"] if d else "-"))
        self.tree.insert("", tk.END, values=("Time (ms)", 
                                            f"{b['elapsed_time']*1000:.1f}" if b else "-", 
                                            f"{d['elapsed_time']*1000:.1f}" if d else "-"))
        
        # Dynamic Conclusion
        if b and d and b["found"] and d["found"]:
            if b["path_length"] < d["path_length"]:
                self.conclusion_var.set("Conclusion: BFS found a shorter path but typically explores more nodes layer-by-layer.")
            elif b["path_length"] == d["path_length"]:
                self.conclusion_var.set("Conclusion: Both algorithms found paths of equal length.")
            else:
                self.conclusion_var.set("Conclusion: DFS found a path, but BFS is guaranteed to be optimal.")

    def animate_search(self, result, algo_name):
        self.is_running = True
        visited = result["visited_order"]
        path = result["path"]
        
        # Animate exploration
        for i, (r, c) in enumerate(visited):
            if (r, c) != self.start_pos and (r, c) != self.goal_pos:
                self.canvas.itemconfig(self.rects[r][c], fill="#f39c12") # Orange/Yellow
                self.live_nodes_var.set(f"Nodes Explored: {i+1}")
                self.curr_node_var.set(f"Current: ({r},{c})")
                if i % 2 == 0: 
                    self.root.update()
                    time.sleep(self.animation_speed.get())
        
        # Animate final path
        if path:
            for r, c in path:
                if (r, c) != self.start_pos and (r, c) != self.goal_pos:
                    self.canvas.itemconfig(self.rects[r][c], fill="blue")
                    self.root.update()
                    time.sleep(self.animation_speed.get() * 2)
        else:
            self.conclusion_var.set("NO PATH FOUND!")
            messagebox.showwarning("Search Complete", f"{algo_name}: No valid path exists.")
        
        self.log_result(algo_name, result)
        self.is_running = False

    def run_bfs(self):
        if self.is_running: return
        self.reset_path()
        res = bfs(self.grid_data, self.start_pos, self.goal_pos, self.allow_diagonal.get())
        self.last_bfs_res = res
        self.animate_search(res, "BFS")
        self.update_table()

    def run_dfs(self):
        if self.is_running: return
        self.reset_path()
        res = dfs(self.grid_data, self.start_pos, self.goal_pos, self.allow_diagonal.get())
        self.last_dfs_res = res
        self.animate_search(res, "DFS")
        self.update_table()

    def run_comparison(self):
        if self.is_running: return
        self.reset_path()
        # Run BFS
        res_bfs = bfs(self.grid_data, self.start_pos, self.goal_pos, self.allow_diagonal.get())
        self.last_bfs_res = res_bfs
        self.animate_search(res_bfs, "BFS")
        
        time.sleep(1) # Pause before next
        self.reset_path()
        
        # Run DFS
        res_dfs = dfs(self.grid_data, self.start_pos, self.goal_pos, self.allow_diagonal.get())
        self.last_dfs_res = res_dfs
        self.animate_search(res_dfs, "DFS")
        
        self.update_table()
