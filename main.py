from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.config import ShariaCryptoCheckerAPP

from routers.manager_router import router as manager_router
from routers.sharia_module_router import router as sharia_module_router
from resources.manager.manager_service import ManagerService

app = ShariaCryptoCheckerAPP

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


app.include_router(manager_router, prefix="/manager")
app.include_router(sharia_module_router, prefix="/sharia_module")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


"""
Program from start to finish

Loads module_service -> loads module_manager

-> module manager
    Loads all modules
    inside each module:
        [MODULE.START]
        check IF active. 
        if active:
            get last checkpoint (previous state) IF APPLICABLE
            gets deactivated?
                save state (if necessary)
            once done checking:
                save current_dt (what was the time when it checked)
                
            
-> api
    module_manager_route
        want to deactivate a module?
            run module_manager.deactivate(module)
                -> updates module._lock (module.deactivate())
                
        change next_schedule (run interval) for a module?
            run module.change_settings(module)
                
    run specific operation?
        module.run_one()
        module.run()
            consist of multiple run_one´s but takes into account that
            the module could be deactivated at any time.
            
    
    get module_settings?
        module.get_module_settings
        
    update module settings
        module.update_module_settings()
        (key, value)
        saves back to json.
        
    
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8080)
