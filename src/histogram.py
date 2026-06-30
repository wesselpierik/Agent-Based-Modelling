import io
import base64
import numpy as np
from target import Target

import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from mesa.visualization.modules import TextElement

class HistogramModule(TextElement):
    def __init__(self):
        super().__init__()

    def render(self, model):
        # Extract data
        target_vals = [
            agent.attentiveness 
            for agent in model.agents 
            if hasattr(agent, 'attentiveness') and type(agent).__name__ == "Target"
        ]

        thief_vals = [
            agent.riskiness 
            for agent in model.agents 
            if hasattr(agent, 'riskiness') and type(agent).__name__ == "Thief"
        ]

        # Create 1 row, 2 columns for side-by-side histograms
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
        
        # Plot 1: Attentiveness
        ax1.hist(target_vals, bins=np.linspace(0, 1, 11), color="brown", edgecolor="white", alpha=0.8)
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, max(20, model.n_targets // 2)) # Safeguard division by zero or very small numbers
        ax1.set_title("Target Attentiveness Distribution", fontsize=11, fontweight='bold')
        ax1.set_xlabel("Attentiveness Score")
        ax1.set_ylabel("Number of Targets")
        ax1.grid(axis='y', alpha=0.2)

        # Plot 2: Riskiness
        ax2.hist(thief_vals, bins=np.linspace(0, 1, 11), color="#2c3e50", edgecolor="white", alpha=0.8)
        ax2.set_xlim(0, 1)
        n_thieves = getattr(model, 'n_thieves', 50) 
        ax2.set_ylim(0, max(20, n_thieves // 2))
        ax2.set_title("Thief Riskiness Distribution", fontsize=11, fontweight='bold')
        ax2.set_xlabel("Riskiness Score")
        ax2.set_ylabel("Number of Thieves")
        ax2.grid(axis='y', alpha=0.2)

        plt.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig) 
        buf.seek(0)
        
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        
        return f'<div style="text-align:center; margin: 15px 0;"><img src="data:image/png;base64,{img_str}" /></div>'