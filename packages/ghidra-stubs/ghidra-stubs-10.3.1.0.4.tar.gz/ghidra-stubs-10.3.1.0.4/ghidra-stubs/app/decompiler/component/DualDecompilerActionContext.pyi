import docking
import ghidra.app.context
import ghidra.app.util.viewer.util
import java.awt
import java.awt.event
import java.lang


class DualDecompilerActionContext(docking.ActionContext, ghidra.app.context.RestrictedAddressSetContext, ghidra.app.util.viewer.util.CodeComparisonPanelActionContext):
    """
    Action context for a dual decompiler panel.
    """





    def __init__(self, provider: docking.ComponentProvider, cPanel: ghidra.app.decompiler.component.CDisplayPanel, source: java.awt.Component):
        """
        Creates an action context for a dual decompiler panel.
        @param provider the provider for this context
        @param cPanel the decompiler panel associated with this context
        @param source the source of the action
        """
        ...



    def equals(self, __a0: object) -> bool: ...

    def getClass(self) -> java.lang.Class: ...

    def getCodeComparisonPanel(self) -> ghidra.app.util.viewer.util.CodeComparisonPanel: ...

    def getComponentProvider(self) -> docking.ComponentProvider:
        """
        Returns the {@link ComponentProvider} that generated this ActionContext
        @return the provider
        """
        ...

    def getContextObject(self) -> object:
        """
        Returns the object that was included by the ComponentProvider when this context was created.
        @return the object that was included by the ComponentProvider when this context was created.
        """
        ...

    def getEventClickModifiers(self) -> int:
        """
        Returns the click modifiers for this event.
         <p>
         Only present for some mouse assisted events, e.g. clicking on a toolbar button or choosing
         a menu item in a popup menu.
        @return bit-masked int, see {@link InputEvent#SHIFT_MASK}, etc
        """
        ...

    def getGlobalContext(self) -> docking.ActionContext:
        """
        Returns the global action context for the tool.  The global context is the context of
         the default focused component, instead of the normal action context which is the current
         focused component.
        @return the global action context for the tool
        """
        ...

    def getMouseEvent(self) -> java.awt.event.MouseEvent:
        """
        Returns the context's mouse event.  Contexts that are based upon key events will have no 
         mouse event.
        @return the mouse event that triggered this context; null implies a key event-based context
        """
        ...

    def getSourceComponent(self) -> java.awt.Component:
        """
        Returns the component that is the target of this context.   This value should not change
         whether the context is triggered by a key binding or mouse event.
        @return the component; may be null
        """
        ...

    def getSourceObject(self) -> object:
        """
        Returns the sourceObject from the actionEvent that triggered this context to be generated.
        @return the sourceObject from the actionEvent that triggered this context to be generated.
        """
        ...

    def hasAnyEventClickModifiers(self, modifiersMask: int) -> bool:
        """
        Tests the click modifiers for this event to see if they contain any bit from the
         specified modifiersMask parameter.
        @param modifiersMask bitmask to test
        @return boolean true if any bit in the eventClickModifiers matches the mask
        """
        ...

    def hashCode(self) -> int: ...

    def notify(self) -> None: ...

    def notifyAll(self) -> None: ...

    def setCodeComparisonPanel(self, codeComparisonPanel: ghidra.app.util.viewer.util.CodeComparisonPanel) -> None:
        """
        Sets the CodeComparisonPanel associated with this context.
        @param codeComparisonPanel the code comparison panel.
        """
        ...

    def setContextObject(self, contextObject: object) -> docking.ActionContext:
        """
        Sets the context object for this context.  This can be any object of the creator's 
         choosing that can be provided for later retrieval.
        @param contextObject Sets the context object for this context.
        @return this context
        """
        ...

    def setEventClickModifiers(self, modifiers: int) -> None:
        """
        Sets the modifiers for this event that were present when the item was clicked on.
        @param modifiers bit-masked int, see {@link ActionEvent#getModifiers()} or
         {@link MouseEvent#getModifiersEx()}
        """
        ...

    def setMouseEvent(self, e: java.awt.event.MouseEvent) -> docking.ActionContext:
        """
        Updates the context's mouse event.  Contexts that are based upon key events will have no 
         mouse event.   This method is really for the framework to use.  Client calls to this 
         method will be overridden by the framework when menu items are clicked.
        @param e the event that triggered this context.
        @return this context
        """
        ...

    def setSourceObject(self, sourceObject: object) -> docking.ActionContext:
        """
        Sets the sourceObject for this ActionContext.  This method is used internally by the 
         DockingWindowManager. ComponentProvider and action developers should only use this 
         method for testing.
        @param sourceObject the source object
        @return this context
        """
        ...

    def toString(self) -> unicode: ...

    @overload
    def wait(self) -> None: ...

    @overload
    def wait(self, __a0: long) -> None: ...

    @overload
    def wait(self, __a0: long, __a1: int) -> None: ...

    @property
    def codeComparisonPanel(self) -> ghidra.app.util.viewer.util.CodeComparisonPanel: ...

    @codeComparisonPanel.setter
    def codeComparisonPanel(self, value: ghidra.app.util.viewer.util.CodeComparisonPanel) -> None: ...