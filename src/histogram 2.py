import io
import base64
import numpy as np
from victim import Victim

import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from mesa.visualization.modules import TextElement

class HistogramModule(TextElement):
    def __init__(self):
        super().__init__()

    def render(self, model):
        # Dynamically extract attentiveness values from your Victim agents
        values = [
            agent.attentiveness 
            for agent in model.agents 
            if hasattr(agent, 'attentiveness') and type(agent).__name__ == "Victim"
        ]

        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.hist(values, bins=np.linspace(0, 1, 11), color="brown", edgecolor="white", alpha=0.8)

        ax.set_xlim(0, 1)
        ax.set_ylim(0, model.n_victims//2)
        ax.set_title("Victim Attentiveness Distribution", fontsize=12, fontweight='bold')
        ax.set_xlabel("Attentiveness Score")
        ax.set_ylabel("Number of Victims")
        ax.grid(axis='y', alpha=0.2)
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig) 
        buf.seek(0)
        
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        
        return f'<div style="text-align:center; margin: 15px 0;"><img src="data:image/png;base64,{img_str}" /></div>'