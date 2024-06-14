def figDesign(fig, title):
    transparent_bg = {
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)"
    }

    fig.update_layout(
        transparent_bg,
        height=500,
        title = {
            "text": title,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18 }
        },
        title_font=dict(color='white', size=20),  # Impostazione del colore e della dimensione del titolo
        font=dict(color='white', size=12),  # Impostazione del colore e della dimensione del testo generale
        xaxis=dict(title_font=dict(color='white', size=14)),  # Impostazione del colore e della dimensione dell'asse x
        yaxis=dict(title_font=dict(color='white', size=14)),
        )
    
colors = {
            "count_position_1": "gold",
            "count_position_2": "silver",
            "count_position_3": "peru"
        }