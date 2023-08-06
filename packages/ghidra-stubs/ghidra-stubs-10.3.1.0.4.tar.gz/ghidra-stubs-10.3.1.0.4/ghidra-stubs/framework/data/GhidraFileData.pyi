import ghidra.framework.data
import ghidra.framework.model
import java.lang


class GhidraFileData(object):
    CHECKED_OUT_EXCLUSIVE_ICON: javax.swing.Icon = jar:file:/opt/hostedtoolcache/ghidra/10.3/x64/Ghidra/Framework/Gui/lib/Gui.jar!/images/core.png
    CHECKED_OUT_ICON: javax.swing.Icon = jar:file:/opt/hostedtoolcache/ghidra/10.3/x64/Ghidra/Framework/Gui/lib/Gui.jar!/images/core.png
    HIJACKED_ICON: javax.swing.Icon = jar:file:/opt/hostedtoolcache/ghidra/10.3/x64/Ghidra/Framework/Gui/lib/Gui.jar!/images/core.png
    NOT_LATEST_CHECKED_OUT_ICON: javax.swing.Icon = jar:file:/opt/hostedtoolcache/ghidra/10.3/x64/Ghidra/Framework/Gui/lib/Gui.jar!/images/core.png
    READ_ONLY_ICON: javax.swing.Icon = jar:file:/opt/hostedtoolcache/ghidra/10.3/x64/Ghidra/Framework/Gui/lib/Gui.jar!/images/core.png
    UNSUPPORTED_FILE_ICON: javax.swing.Icon = jar:file:/opt/hostedtoolcache/ghidra/10.3/x64/Ghidra/Framework/Gui/lib/Gui.jar!/images/core.png
    VERSION_ICON: javax.swing.Icon = ghidra.framework.data.VersionIcon@27f4fd91







    def copyToAsLink(self, newParentData: ghidra.framework.data.GhidraFolderData) -> ghidra.framework.model.DomainFile: ...

    def equals(self, __a0: object) -> bool: ...

    def getClass(self) -> java.lang.Class: ...

    def hashCode(self) -> int: ...

    def isLinkingSupported(self) -> bool: ...

    def notify(self) -> None: ...

    def notifyAll(self) -> None: ...

    def toString(self) -> unicode: ...

    @overload
    def wait(self) -> None: ...

    @overload
    def wait(self, __a0: long) -> None: ...

    @overload
    def wait(self, __a0: long, __a1: int) -> None: ...

    @property
    def linkingSupported(self) -> bool: ...