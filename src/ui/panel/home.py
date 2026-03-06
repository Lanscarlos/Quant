from nicegui import ui, app as nicegui_app

# nicegui_app.add_static_files('/assets', 'assets')
nicegui_app.add_static_file(local_file='assets/lottie/loading_animation_blue.json', url_path='/assets/lottie/loading_animation_blue.json')

def render():
    ui.add_head_html('<script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>')

    ui.label('📋 主面板').classes('text-2xl font-bold')
    ui.separator()
    ui.label('这里是主要内容区域')

    with ui.element('div').props('id=lottie-box').style('width:300px;height:300px;'):
        pass

    ui.run_javascript('''
          lottie.loadAnimation({
            container: document.getElementById("lottie-box"),
            renderer: "svg",
            loop: true,
            autoplay: true,
            path: "/assets/lottie/loading_animation_blue.json"
          });
        ''')
