from typing import List
import com.google.gson
import ghidra.framework.options
import java.awt
import java.io
import java.lang
import java.util
import javax.swing
import org.jdom


class SaveState(object):
    """
    Class for saving name/value pairs as XML or Json.  Classes that want to be
     able to save their state can do so using the SaveState object.
     The idea is that each state variable in the class
     is first saved into a SaveState object via a String key.  Then the SaveState
     object is written out as XML or Json.  When the save state object is
     restored, the SaveState object is constructed with an XML Element or JsonObject
     that contains all of the name/value pairs. Since the "get" methods require
     a default value, the object that is recovering its state variables
     will be successfully initialized even if
     the given key,value pair is not found in the SaveState object.
      Note: Names for options are assumed to be unique. When a putXXX()
     method is called, if a value already exists for a name, it will
     be overwritten.
 
     The SaveState supports the following types:
 
          java primitives
          arrays of java primitives
          String
          Color
          Font
          KeyStroke
          File
          Date
          Enum
          SaveState (values can be nested SaveStates)
  
    """

    DATE_FORMAT: java.text.DateFormat



    @overload
    def __init__(self):
        """
        Default Constructor for SaveState; uses "SAVE_STATE" as the
         name of the state.
        @see java.lang.Object#Object()
        """
        ...

    @overload
    def __init__(self, name: unicode):
        """
        Creates a new SaveState object with a non-default name.  The name serves no real purpose
         other than as a hint as to what the SaveState represents
        @param name of the state
        """
        ...

    @overload
    def __init__(self, file: java.io.File):
        """
        Construct a SaveState from a file containing XML from a previously saved SaveState.
        @param file the file containing the XML to read.
        @throws IOException if the file can't be read or is not formatted properly for a SaveState
        """
        ...

    @overload
    def __init__(self, root: org.jdom.Element):
        """
        Construct a new SaveState object using the given XML element.
        @param root XML contents of the save state
        """
        ...



    def clear(self) -> None:
        """
        Clear all objects from the save state.
        """
        ...

    def equals(self, __a0: object) -> bool: ...

    def getBoolean(self, name: unicode, defaultValue: bool) -> bool:
        """
        Gets the boolean value for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the boolean value associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getBooleans(self, name: unicode, defaultValue: List[bool]) -> List[bool]:
        """
        Gets the boolean array for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the boolean array associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getByte(self, name: unicode, defaultValue: int) -> int:
        """
        Gets the byte value for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the byte value associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getBytes(self, name: unicode, defaultValue: List[int]) -> List[int]:
        """
        Gets the byte array for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the byte array associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getClass(self) -> java.lang.Class: ...

    def getColor(self, name: unicode, defaultValue: java.awt.Color) -> java.awt.Color:
        """
        Gets the Color value for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the Color value associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getDate(self, name: unicode, defaultValue: java.util.Date) -> java.util.Date:
        """
        Gets the Date value for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the Date value associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getDouble(self, name: unicode, defaultValue: float) -> float:
        """
        Gets the double value for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the double value associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getDoubles(self, name: unicode, defaultValue: List[float]) -> List[float]:
        """
        Gets the double array for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the double array associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getEnum(self, __a0: unicode, __a1: java.lang.Enum) -> java.lang.Enum: ...

    def getFile(self, name: unicode, defaultValue: java.io.File) -> java.io.File:
        """
        Gets the File value for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the File value associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getFloat(self, name: unicode, defaultValue: float) -> float:
        """
        Gets the float value for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the float value associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getFloats(self, name: unicode, defaultValue: List[float]) -> List[float]:
        """
        Gets the float array for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the float array associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getFont(self, name: unicode, defaultValue: java.awt.Font) -> java.awt.Font:
        """
        Gets the Font value for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the Font value associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getInt(self, name: unicode, defaultValue: int) -> int:
        """
        Gets the int value for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the int value associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getInts(self, name: unicode, defaultValue: List[int]) -> List[int]:
        """
        Gets the int array for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the int array associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getKeyStroke(self, name: unicode, defaultValue: javax.swing.KeyStroke) -> javax.swing.KeyStroke:
        """
        Gets the KeyStroke value for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the KeyStroke value associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getLong(self, name: unicode, defaultValue: long) -> long:
        """
        Gets the long value for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the long value associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getLongs(self, name: unicode, defaultValue: List[long]) -> List[long]:
        """
        Gets the long array for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the long array associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getNames(self) -> List[unicode]:
        """
        Return the names of the objects saved in the state.
        @return String[] array will be zero length if the save state
         is empty
        """
        ...

    def getSaveState(self, name: unicode) -> ghidra.framework.options.SaveState:
        """
        Returns the sub SaveState associated with the
         given name.
        @param name The name associated with the desired Element.
        @return The SaveState object associated with the
         given name.
        """
        ...

    def getShort(self, name: unicode, defaultValue: int) -> int:
        """
        Gets the short value for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the short value associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getShorts(self, name: unicode, defaultValue: List[int]) -> List[int]:
        """
        Gets the short array for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the short array associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getString(self, name: unicode, defaultValue: unicode) -> unicode:
        """
        Gets the String value for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the String value associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getStrings(self, name: unicode, defaultValue: List[unicode]) -> List[unicode]:
        """
        Gets the String array for the given name.
        @param name the name of the pair.
        @param defaultValue the default value to be returned if the name does
         not exist in the map, or it does not contain the proper object type.
        @return the String array associated with the given name or the defaultValue
         passed in if the name doesn't exist or is the wrong type.
        """
        ...

    def getXmlElement(self, name: unicode) -> org.jdom.Element:
        """
        Returns the root of an XML sub-tree associated with the
         given name.
        @param name The name associated with the desired Element.
        @return The root of an XML sub-tree associated with the
         given name.
        """
        ...

    def hasValue(self, name: unicode) -> bool:
        """
        Returns true if there is a value for the given name
        @param name true the name of the property to check for a value
        @return true if the SaveState object has a value for the given name
        """
        ...

    def hashCode(self) -> int: ...

    def isEmpty(self) -> bool:
        """
        Returns true if this list contains no elements
        @return true if there are no properties in this save  state
        """
        ...

    def notify(self) -> None: ...

    def notifyAll(self) -> None: ...

    def putBoolean(self, name: unicode, value: bool) -> None:
        """
        Associates a boolean value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putBooleans(self, name: unicode, value: List[bool]) -> None:
        """
        Associates a boolean array with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putByte(self, name: unicode, value: int) -> None:
        """
        Associates a byte value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putBytes(self, name: unicode, value: List[int]) -> None:
        """
        Associates a byte array with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putColor(self, name: unicode, value: java.awt.Color) -> None:
        """
        Associates a Color value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putDate(self, name: unicode, value: java.util.Date) -> None:
        """
        Associates a Date value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putDouble(self, name: unicode, value: float) -> None:
        """
        Associates a double value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putDoubles(self, name: unicode, value: List[float]) -> None:
        """
        Associates a double value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putEnum(self, name: unicode, value: java.lang.Enum) -> None:
        """
        Associates an Enum with the given name.
        @param name The name in the name,value pair.
        @param value The Enum value in the name,value pair.
        """
        ...

    def putFile(self, name: unicode, value: java.io.File) -> None:
        """
        Associates a File value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putFloat(self, name: unicode, value: float) -> None:
        """
        Associates a float value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putFloats(self, name: unicode, value: List[float]) -> None:
        """
        Associates a float array with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putFont(self, name: unicode, value: java.awt.Font) -> None:
        """
        Associates a Font value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putInt(self, name: unicode, value: int) -> None:
        """
        Associates an integer value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putInts(self, name: unicode, value: List[int]) -> None:
        """
        Associates an integer array with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putKeyStroke(self, name: unicode, value: javax.swing.KeyStroke) -> None:
        """
        Associates a KeyStroke value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putLong(self, name: unicode, value: long) -> None:
        """
        Associates a long value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putLongs(self, name: unicode, value: List[long]) -> None:
        """
        Associates a long array with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putSaveState(self, name: unicode, value: ghidra.framework.options.SaveState) -> None:
        """
        Associates a sub SaveState value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putShort(self, name: unicode, value: int) -> None:
        """
        Associates a short value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putShorts(self, name: unicode, value: List[int]) -> None:
        """
        Associates a short array with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putString(self, name: unicode, value: unicode) -> None:
        """
        Associates a String value with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putStrings(self, name: unicode, value: List[unicode]) -> None:
        """
        Associates a String array with the given name.
        @param name The name in the name,value pair.
        @param value The value in the name,value pair.
        """
        ...

    def putXmlElement(self, name: unicode, element: org.jdom.Element) -> None:
        """
        Adds an XML element to the
         saved state object. Used by plugins that have more
         complicated state information that needs to be saved.
        @param name the name to associate with the element
        @param element XML element which is the root of an
         XML sub-tree.
        """
        ...

    @staticmethod
    def readJsonFile(file: java.io.File) -> ghidra.framework.options.SaveState:
        """
        Creates a SaveState object and populates its values from the given file. The file must 
         conform to the format that is created with {@link #saveToJson()}
        @param file the file to load values from
        @return a new SaveState object loaded with values from the given file.
        @throws IOException if an error occurs reading the given file.
        """
        ...

    def remove(self, name: unicode) -> None:
        """
        Remove the object identified by the given name
        @param name the name of the property to remove
        """
        ...

    def saveToFile(self, file: java.io.File) -> None:
        """
        Write the saveState to a file as XML
        @param file the file to write to.
        @throws FileNotFoundException if the file does not represent a valid file path.
        @throws IOException if the file could not be written
        """
        ...

    def saveToJson(self) -> com.google.gson.JsonObject:
        """
        Save this object to an JsonObject
        @return JsonObject containing the state
        """
        ...

    def saveToJsonFile(self, file: java.io.File) -> None:
        """
        Outputs this SaveState to a file using Json
         <P>
         For example, a SaveState that is created with:
         <pre>
          ss = new SaveState("foo")
        	ss.putString("Name", "Bob");
        	ss.putBoolean("Retired", true);
        	ss.putInt("Age", 65);
        	ss.putEnum("Endian", Endian.BIG);

          would produce a Json file with the following text

         {
          "SAVE STATE NAME": "foo",
          "VALUES": {
            "Name": "Bob"
            "Retired": true,
            "Age": 65,
            "Endian": "BIG",
          },
          "TYPES": {
            "Name": "String"
            "Retired": "boolean",
            "Age": "int",
            "Endian": "enum",
          },	
          "ENUM CLASSES": {
            "Endian": "ghidra.program.model.lang.Endian"
          }
        }
         </pre>
        @param file the file to save to
        @throws IOException if an error occurs writing to the given file
        """
        ...

    def saveToXml(self) -> org.jdom.Element:
        """
        Save this object to an XML element.
        @return Element XML element containing the state
        """
        ...

    def size(self) -> int:
        """
        Return the number of properties in the save state
        @return The number of properties in the save state
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
    def empty(self) -> bool: ...

    @property
    def names(self) -> List[unicode]: ...