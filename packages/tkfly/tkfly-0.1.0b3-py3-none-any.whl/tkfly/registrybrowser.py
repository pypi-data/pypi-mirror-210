import tkinter as tk
import tkfly
from tkfly._tktreectrl import _load_tktreectrl

root = tk.Tk()
_load_tktreectrl()
root.eval("""
package require Tcl 8.6
package require Tk 8.6

#console show

package require registry

# registry base keys
set BaseKeys {
        HKEY_LOCAL_MACHINE
        HKEY_USERS
        HKEY_CLASSES_ROOT
        HKEY_CURRENT_USER
        HKEY_CURRENT_CONFIG
}

set type_map {
        none                                 REG_NONE
        sz                                         REG_SZ
        expand_sz                        REG_EXPAND_SZ
        binary                                REG_BINARY
        dword_big_endian        REG_DWORD
        dword                                REG_DWORD_LITTLE_ENDIAN
        link                                REG_LINK
        multi_sz                        REG_MULTI_SZ
        resource_list                REG_RESOURCE_LIST
        9                                        REG_FULL_RESOURCE_DESCRIPTOR
}

font create datafont -family Courier  -size 10

proc create-tree-gui { win name } {
        labelframe ${win} -text ${name}
        treectrl ${win}.t -showroot no -width 400 -height 300
        scrollbar ${win}.y -ori vertical   -command [list ${win}.t yview]
        scrollbar ${win}.x -ori horizontal -command [list ${win}.t xview]
        grid ${win}.t ${win}.y -sticky news
        grid ${win}.x  -sticky news
        grid configure ${win}.t -row 0 -column 0 -sticky news
        grid configure ${win}.y        -row 0 -column 1
        grid configure ${win}.x -row 1 -column 0 -sticky news
        grid columnconfig ${win} 0 -weight 1
        grid columnconfig ${win} 1 -weight 0
        grid rowconfig ${win} 0 -weight 1
        grid rowconfig ${win} 1 -weight 0
        return ${win}.t
}

proc initialize-tree { win } {
        set treeCol [${win} column create]
        ${win} configure -treecolumn $treeCol

        # normal
        ${win} element create elemBorder border
        ${win} element configure elemBorder -background #ece9d8 -filled yes -relief solid -thickness 1
        ${win} element create elemText text
        ${win} style create treeStyle
        ${win} style elements treeStyle {elemBorder elemText}
        ${win} style layout treeStyle elemBorder -union {elemText} -ipadx 4 -ipady 1 -pady 2
        ${win} style layout treeStyle elemText
        ${win} item configure root -button no
        ${win} item style set root $treeCol treeStyle
        ${win} item element configure root $treeCol elemText -text "Base Keys"

        foreach key $::BaseKeys {
                set itemID [${win} item create -button yes]
                ${win} item collapse $itemID
                ${win} item style set $itemID last treeStyle
                ${win} item element configure $itemID last elemText -text ${key}
                ${win} item lastchild root $itemID
        }         
        ${win} notify bind ${win} <ActiveItem> {
                render-item %T %c %p
        }
        ${win} notify bind ${win} <Expand-before> {
                AddChildItems %T %I
        }
}

proc initialize-values { win } {
        ${win} column create
        
        # create value/type style
        ${win} element create nameBorder border -background black -filled no -relief solid -thickness 1
        ${win} element create nameText text
        ${win} element create typeBorder border -background #ece9d8 -filled yes -relief solid -thickness 1
        ${win} element create typeText text
        ${win} style create value_style1
        ${win} style elements value_style1 {nameBorder nameText typeBorder typeText}
        ${win} style layout value_style1 nameBorder -union {nameText} -ipadx 4 -ipady 2 -pady 2
        ${win} style layout value_style1 typeBorder -union {typeText} -ipadx 4 -ipady 2 -padx 10 -pady 2
        
        # create data style
        ${win} element create dataBorder border -background #ece9d8 -filled no -relief solid -thickness 1
        ${win} element create dataText text -font datafont
        ${win} style create dataStyle
        ${win} style elements dataStyle {dataBorder dataText}
        ${win} style layout dataStyle dataBorder -union {dataText} -ipadx 6 -ipady 4 -padx 10 -pady 1
        ${win} style layout dataStyle dataText
        
        # create red data style
        ${win} element create redDataBorder border -background #ff8f8f -filled yes -relief solid -thickness 1
        ${win} style create redDataStyle
        ${win} style elements redDataStyle {redDataBorder dataText}
        ${win} style layout redDataStyle redDataBorder -union {dataText} -ipadx 6 -ipady 4 -padx 10 -pady 1
        ${win} style layout redDataStyle dataText
}

proc AddChildItems {tree parent} {
        if {[$tree item numchildren $parent] > 0} return
        set path [get-item-text $tree $parent]
        set parent-key [get-tree-path ${path} $tree $parent]

        if { [catch {registry keys ${parent-key}} keys] } {
                tk_messageBox -icon error -title "Registry Lookup Failed" -message \
                        "Unable to get keys from registry.\nKey: ${parent-key}\nError: ${keys}"
        } else {
                foreach key ${keys} {
                        set itemID [$tree item create -button yes]
                        $tree item collapse $itemID
                        $tree item style set $itemID last treeStyle
                        $tree item element configure $itemID last elemText -text ${key}
                        $tree item lastchild $parent $itemID
                        
                        set k "${parent-key}\\${key}"
                        if { [catch {registry keys ${k}} dummy] } {
                                set bval no
                        } else {
                                if { [llength ${dummy}] > 0 } {
                                        set bval yes
                                } else {
                                        set bval no
                                }
                        }
                        $tree item configure $itemID -button ${bval}
                }
        }

        return
}

proc get-item-text {tree item} {
        lassign [$tree item rnc $item] row col
        set pkey {}
        if { ${col} ne "" } {
                set pkey [${::t-tree} item element cget $item $col elemText -text]
        }
        #puts "${tree} ${item} rnc($row,$col) pkey($pkey)"
        return $pkey
}
proc get-item-parent {tree item} {
        return [$tree item parent $item]
}
proc get-tree-path {path tree item} {
        set p-item [get-item-parent $tree $item]
        set p-text [get-item-text $tree ${p-item}]
        if { ${p-text} eq "" } {
                # done
                return [join ${path} "\\"]
        } else {
                set path [linsert ${path} 0 ${p-text}]
                return [get-tree-path ${path} ${tree} ${p-item}]
        }
}

proc put-value {name vtype data {red 0}} {
        set itemID [${::v-tree} item create]
        ${::v-tree} item style set $itemID first value_style1
        ${::v-tree} item element configure $itemID first nameText -text ${name}
        ${::v-tree} item element configure $itemID first typeText -text ${vtype}
        ${::v-tree} item lastchild root $itemID
        
        set itemID [${::v-tree} item create]
        if { ${red} eq 1 } {
                ${::v-tree} item style set $itemID first redDataStyle
        } else {
                ${::v-tree} item style set $itemID first dataStyle
        }
        ${::v-tree} item element configure $itemID first dataText -text ${data}
        ${::v-tree} item lastchild root $itemID
}

proc render-item { tree item prev_item } {
        # highlight selected tree item
        ${::t-tree} item element configure $prev_item last elemBorder -background #ece9d8
        ${::t-tree} item element configure $item last elemBorder -background #cfcfff
        
        # clear value display
        foreach i [${::v-tree} item children root] {
                ${::v-tree} item delete ${i}
        }
        
        # display new values
        set path [get-item-text $tree $item]
        set key [get-tree-path ${path} $tree $item]

        if { [catch {registry values $key} names] } {
                put-value $path "REG_NONE" "{access denied}" 1
        } else {
                # add default value to names list
                lappend names ""
                foreach name [lsort -dictionary -unique $names] {
                        # key HKEY_CLASSES_ROOT\\* name AlwaysShowExt
                        if { [catch {registry type $key $name} t] } {
                                set t "sz"
                        }
                        set _type [string map $::type_map $t]
                        if { [catch {registry get $key $name} data] } {
                                set data "{value not set}"
                        }
                        if { ${name} eq "" } {
                                set name "{default}"
                        }
                        switch -exact -- $_type {
                                REG_BINARY -
                                REG_FULL_RESOURCE_DESCRIPTOR {
                                        set data [hexdump ${data}]
                                }
                                REG_FULL_RESOURCE_DESCRIPTOR -
                                REG_DWORD_LITTLE_ENDIAN -
                                REG_MULTI_SZ -
                                REG_SZ {
                                }
                                default {
                                }
                        }
                        put-value $name ${_type} ${data}
                }
        }
}

proc hexdump { data } {
        set buf ""
        for {set i 0} {$i < [string length $data]} {incr i 16} {
                set row [string range $data $i [expr {$i + 15}]]
                binary scan $row H* hex
                set hex [regsub -all {(.{4})} [format %-32s $hex] {\1 }]
                set row [regsub -all {[^[:print:]]} $row .]
                append buf [format "%08x: %s %-16s\n" $i $hex $row]
        }
        return [string trimright ${buf}]
}

###########################################################################

set pwin [panedwindow .pw -orient horizontal]

set t-tree [create-tree-gui ${pwin}.t "Registry"]
set v-tree [create-tree-gui ${pwin}.v "Values"]

${pwin} add ${pwin}.t ${pwin}.v

pack ${pwin} -expand yes -fill both

initialize-tree ${t-tree}
initialize-values ${v-tree}
""")
root.mainloop()