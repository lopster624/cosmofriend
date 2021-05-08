var player = new Playerjs({
        id:"player",
        file:[
            {% for video in videos%}
            {"title":"{{video.title}}","file":"{{video.video.url}}"},
            {%endfor%}
        ]
        });