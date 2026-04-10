import matplotlib.pyplot as plt
import base64
from io import BytesIO
import matplotlib.ticker as ticker

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight') # bbox_inches='tight' se text kat-ta nahi hai
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

# 1. NORMAL TREND GRAPH (30 Days) - Date Overlap Fixed
def get_plot(x, y, title):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 5))
    plt.title(title, fontsize=14, fontweight='bold', color='#333')
    
    # Plotting
    plt.plot(x, y, color='#b8860b', marker='o', linestyle='-', linewidth=2, markersize=6)
    plt.fill_between(x, y, color='#b8860b', alpha=0.1) # Thoda gold shade neeche
    
    # 🔥 FIX: Dates ko 45 degree rotate karo taaki takraye nahi
    plt.xticks(rotation=45, ha='right', fontsize=9)
    
    # 🔥 FIX: Agar zyada dates hain to har 3rd date dikhao
    ax = plt.gca()
    if len(x) > 10:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(3))

    plt.ylabel('Sales (₹)', fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    graph = get_graph()
    return graph

# 2. COMPARISON GRAPH (2 Weeks) - New Feature
def get_comparison_plot(data1, data2, label1, label2):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 5))
    plt.title(f'Comparison: {label1} vs {label2}', fontsize=14, fontweight='bold')
    
    days = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7']
    
    # Line 1 (Pehla Week - Gold)
    plt.plot(days, data1, color='#b8860b', marker='o', linestyle='-', linewidth=2, label=label1)
    
    # Line 2 (Dusra Week - Black/Grey)
    plt.plot(days, data2, color='#333333', marker='s', linestyle='--', linewidth=2, label=label2)
    
    plt.legend() # Label dikhane ke liye
    plt.ylabel('Sales (₹)', fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    graph = get_graph()
    return graph