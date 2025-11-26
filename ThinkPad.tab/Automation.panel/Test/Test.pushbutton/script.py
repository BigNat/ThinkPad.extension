# -*- coding: utf-8 -*-
from pyrevit import forms, revit, DB
import os, json

__title__ = "Test"
__doc__ = "Test"

def main():

        forms.alert(
            u"✅ Test completed successfully!",
            title=u"ThinkPad → Test"
        )


if __name__ == "__main__":
    main()
