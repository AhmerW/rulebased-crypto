from core.config import ShariaCryptoCheckerAPP

from routers.checks_router import router as checks_router
from resources.manager.manager_service import ManagerService


app = ShariaCryptoCheckerAPP

app.include_router(checks_router, prefix="/sharia")

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
            
-> api
    module_manager_route
        want to deactivate a module?
            run module_manager.deactivate(module)
                -> updates module._lock (module.deactivate())
                
    run specific operation?
        module.run_one()
        module.run()
            consist of multiple run_one´s but takes into account that
            the module could be deactivated at any time.
        
    
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8080)
