from typing import List
import docking
import docking.widgets.tree
import ghidra.formats.gfilesystem
import ghidra.plugins.fsbrowser
import java.awt
import java.awt.event
import java.lang


class FSBActionContext(docking.ActionContext):
    """
    FileSystemBrowserPlugin-specific action.
    """





    def __init__(self, provider: ghidra.plugins.fsbrowser.FileSystemBrowserComponentProvider, selectedNodes: List[ghidra.plugins.fsbrowser.FSBNode], event: java.awt.event.MouseEvent, gTree: docking.widgets.tree.GTree):
        """
        Creates a new {@link FileSystemBrowserPlugin}-specific action context.
        @param provider the ComponentProvider that generated this context.
        @param selectedNodes selected nodes in the tree
        @param event MouseEvent that caused the update, or null
        @param gTree {@link FileSystemBrowserPlugin} provider tree.
        """
        ...



    def equals(self, __a0: object) -> bool: ...

    def getClass(self) -> java.lang.Class: ...

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

    def getFSRL(self, dirsOk: bool) -> ghidra.formats.gfilesystem.FSRL:
        """
        Returns the {@link FSRL} of the currently selected item, as long as it conforms to
         the dirsOk requirement.
        @param dirsOk boolean flag, if true the selected item can be either a file or directory
         element, if false, it must be a file or the root of a file system that has a container
         file
        @return FSRL of the single selected item, null if no items selected or more than 1 item
         selected
        """
        ...

    def getFSRLs(self, dirsOk: bool) -> List[ghidra.formats.gfilesystem.FSRL]:
        """
        Returns a list of FSRLs of the currently selected nodes in the tree.
        @param dirsOk boolean flag, if true the selected items can be either a file or directory
         element, if false, it must be a file or the root of a file system that has a container
         file before being included in the resulting list
        @return list of FSRLs of the currently selected items, maybe empty but never null
        """
        ...

    def getFileFSRL(self) -> ghidra.formats.gfilesystem.FSRL:
        """
        Returns the FSRL of the currently selected file node
        @return FSRL of the currently selected file, or null if not file or more than 1 selected
        """
        ...

    def getFileFSRLs(self) -> List[ghidra.formats.gfilesystem.FSRL]:
        """
        Returns a list of FSRLs of the currently selected file nodes in the tree.
        @return list of FSRLs of the currently selected file items, maybe empty but never null
        """
        ...

    def getFormattedTreePath(self) -> unicode:
        """
        Converts the tree-node hierarchy of the currently selected item into a string path using
         "/" separators.
        @return string path of the currently selected tree item
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

    def getLoadableFSRL(self) -> ghidra.formats.gfilesystem.FSRL:
        """
        Returns the FSRL of the currently selected item, if it is a 'loadable' item.
        @return FSRL of the currently selected loadable item, or null if nothing selected or
         more than 1 selected
        """
        ...

    def getLoadableFSRLs(self) -> List[ghidra.formats.gfilesystem.FSRL]:
        """
        Returns a list of FSRLs of the currently selected loadable items.
        @return list of FSRLs of currently selected loadable items, maybe empty but never null
        """
        ...

    def getMouseEvent(self) -> java.awt.event.MouseEvent:
        """
        Returns the context's mouse event.  Contexts that are based upon key events will have no 
         mouse event.
        @return the mouse event that triggered this context; null implies a key event-based context
        """
        ...

    def getRootOfSelectedNode(self) -> ghidra.plugins.fsbrowser.FSBRootNode:
        """
        Returns the FSBRootNode that contains the currently selected tree node.
        @return FSBRootNode that contains the currently selected tree node, or null nothing
         selected
        """
        ...

    def getSelectedCount(self) -> int:
        """
        Returns the number of selected nodes in the tree.
        @return returns the number of selected nodes in the tree.
        """
        ...

    def getSelectedNode(self) -> ghidra.plugins.fsbrowser.FSBNode:
        """
        Returns the currently selected tree node
        @return the currently selected tree node, or null if no nodes or more than 1 node is selected
        """
        ...

    def getSelectedNodes(self) -> List[ghidra.plugins.fsbrowser.FSBNode]:
        """
        Returns a list of the currently selected tree nodes.
        @return list of currently selected tree nodes
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

    def getTree(self) -> docking.widgets.tree.GTree:
        """
        Gets the {@link FileSystemBrowserPlugin} provider's  tree.
        @return The {@link FileSystemBrowserPlugin} provider's  tree.
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

    def hasSelectedNodes(self) -> bool:
        """
        Returns true if there are selected nodes in the browser tree.
        @return boolean true if there are selected nodes in the browser tree
        """
        ...

    def hashCode(self) -> int: ...

    def isBusy(self) -> bool:
        """
        Returns true if the GTree is busy
        @return boolean true if the GTree is busy
        """
        ...

    def isSelectedAllDirs(self) -> bool:
        """
        Returns true if the currently selected items are all directory items
        @return boolean true if the currently selected items are all directory items
        """
        ...

    def notBusy(self) -> bool:
        """
        Returns true if the GTree is not busy
        @return boolean true if GTree is not busy
        """
        ...

    def notify(self) -> None: ...

    def notifyAll(self) -> None: ...

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
    def busy(self) -> bool: ...

    @property
    def fileFSRL(self) -> ghidra.formats.gfilesystem.FSRL: ...

    @property
    def fileFSRLs(self) -> List[object]: ...

    @property
    def formattedTreePath(self) -> unicode: ...

    @property
    def loadableFSRL(self) -> ghidra.formats.gfilesystem.FSRL: ...

    @property
    def loadableFSRLs(self) -> List[object]: ...

    @property
    def rootOfSelectedNode(self) -> ghidra.plugins.fsbrowser.FSBRootNode: ...

    @property
    def selectedAllDirs(self) -> bool: ...

    @property
    def selectedCount(self) -> int: ...

    @property
    def selectedNode(self) -> ghidra.plugins.fsbrowser.FSBNode: ...

    @property
    def selectedNodes(self) -> List[object]: ...

    @property
    def tree(self) -> docking.widgets.tree.GTree: ...