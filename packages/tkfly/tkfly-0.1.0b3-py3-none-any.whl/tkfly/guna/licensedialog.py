class FlyGunaLicenseDialog:
    def __init__(self):
        self.init()

    def init(self):
        from tkfly.guna.load import load
        load()
        from Guna.UI2.WinForms import GunaUI_LicenseMgr
        self._widget = GunaUI_LicenseMgr()

    def widget(self):
        return self._widget


