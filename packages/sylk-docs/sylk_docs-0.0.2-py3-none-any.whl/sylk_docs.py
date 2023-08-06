import os
import subprocess
from sylk.builder import hookimpl
from sylk.commons.helpers import SylkJson, SylkContext, Graph,file_system
from sylk.commons.pretty import print_info,print_success,print_warning,print_error

plugin_extension = 'sylk-docs/sylk.Plugin.v1.Plugin'

@hookimpl
def pre_build(sylk_json: SylkJson, sylk_context: SylkContext):
    print_info("🔌 Starting sylk build process %s plugin" % (__name__))
    

@hookimpl
def post_build(sylk_json: SylkJson, sylk_context: SylkContext):
    return (__name__,'OK')

@hookimpl
def pre_build_server(sylk_json: SylkJson, sylk_context: SylkContext):
    print_info("Running pre build server")
    return {
    }

@hookimpl
def pre_build_clients(sylk_json: SylkJson, sylk_context: SylkContext):
    print_info("Running pre build client")
    return {
    }

def dictionary_to_string(dictionary):
    pairs = []
    for key, value in dictionary.items():
        if isinstance(value, list):
            value_str = ','.join(str(v) for v in value)
        else:
            value_str = str(value)
        pairs.append(f"{key}={value_str}")
    return ','.join(pairs)

@hookimpl
def process_plugin(sylk_json: SylkJson, sylk_context: SylkContext):
    
    docker_extensions = [ext for ext in sylk_json.project.get('extensions') if ext.get('@type') == plugin_extension]
    
    print_info('[docs] parsing extensions:')
    for ext in docker_extensions:
        
        if file_system.check_if_dir_exists(file_system.get_current_location()+'/docs') == False:
            print_warning("docs not initialized...")
            docusaurus = ext.get('docusaurus')
            sylk = docusaurus.get('sylk')
            docs = docusaurus.get('docs')
            sylk_json_paths = sylk.get('sylkJsonPaths')
            sylk_docs_path = sylk.get('sylkDocsPath')
            sylk_sidebar_path = sylk.get('sidebarPath')
            sylk_route_path = docs.get('routeBasePath')
            jsons = ''.join(map(lambda x: x,sylk_json_paths,))
            print_warning(f"initalizaing docs at: ./docs")
            process = subprocess.Popen([
                'npm','i','docusaurus-sylk-init',
                
            ],
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)

                        
            _, stderr = process.communicate()
            if stderr:
                print_warning(stderr.decode('utf-8'))
            
            process = subprocess.Popen([
                'npx',
                'docusaurus-sylk-init',
                'init',
                'docs',
                f'--sylk-jsons-paths {jsons}', 
                '--json sylk.json'
                f'--sylk-docs-path {sylk_docs_path}',
                f'--sidebar-path {sylk_sidebar_path}',
                f'--route-base-path {sylk_route_path}',
            ])
            _, stderr = process.communicate()
            if stderr:
                print_warning(stderr.decode('utf-8'))

        else:
            ext_opt_type = ext.get('@type')
            extensions = {}
            print(f'\t- {ext_opt_type}')
            _current = file_system.get_current_location()
            os.chdir(_current+'/docs')
            process = subprocess.Popen(['npx', 'docusaurus','generate-sylk-docs'],
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
            _, stderr = process.communicate()
            if stderr:
                print_warning(stderr.decode('utf-8'))
            os.chdir(_current)

        
    print_success("Running `process_plugin` {}".format(__name__))