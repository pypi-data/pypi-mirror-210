from tkinter import Widget


def _command(*args, **kwargs):
    pass


class Tree(Widget):
    """
    简易树视图控件

    根据https://wiki.tcl-lang.org/page/A+Minimal+Tree+Widget文章修改而来
    """

    def __init__(self, master=None):
        """
        简易示例：

        from tkinter import *
        from tkdev5 import *


        root = Tk()

        tree = DevMinimalTreeView()
        tree.add(0, "First", lambda: print("First"))
        tree.add(1, "Second", lambda: print("Second"))
        tree.add(2, "Third", lambda: print("Third"))
        tree.toggle(1)
        tree.toggle(2)

        root.mainloop()
        """

        MinimalTree = """
 namespace eval ::ttree {}
 image create photo ::ttree::tree-close -data {
   R0lGODdhCQAJAJEAAGZmZv///wAAAP///ywAAAAACQAJAAACGYSPFD8A8IDA
   +AEQJDsAKH4A4AGB8YPgYwEAOw== 
 }
 image create photo ::ttree::tree-open -data {
   R0lGODdhCQAJAJEAAGZmZv///wAAAP///ywAAAAACQAJAAACHoSPFD8ATo6A
   REhEEBCSHQARQUoCICJISQBQ/CD4WAA7 
 }
 image create photo ::ttree::tree-dot -data {
   R0lGODdhCQAJAJEAAP///wAAAP///////ywAAAAACQAJAAACD4SPqXtB8CEg
   8CiEj6l7BQA7 
 }

 proc ::ttree::tree {w args} {
   variable tree;

   ::text $w -cursor {} -spacing3 1p
   if { [llength $args] > 0 } {
        $w configure {*}$args
      }
   set tree($w,items) 0
   set tags [bindtags $w]
   set pos [lsearch -exact $tags "Text"]
   bindtags $w [lreplace $tags $pos $pos]
   bind $w <Destroy> [list array unset ::ttree::tree %W,*]

   $w tag configure sub-0 -elide 0

   return $w;
 };# ttree::tree

 proc ::ttree::add {w parent txt cmd} {
   variable tree;

   if { ![winfo exists $w] || ![info exists tree($w,items)] } {
        error "widget \"$w\" does not exist, or is not a tree widget"
      }

   if { $parent != 0 && ![info exists tree($w,parent,$parent)] } {
        error "tree \"$w\" has no id \"$parent \""
      }

   return [addSub $w $parent $txt $cmd];
 }

 proc ::ttree::addSub {w parent txt cmd} {
   variable tree;

   set new [incr tree($w,items)]
   set tree($w,parent,$new) $parent
   set taglist [list id-$new]
   set tagParent $parent
   while { [info exists tree($w,parent,$tagParent)] } {
           lappend taglist sub-$tagParent
           set tagParent $tree($w,parent,$tagParent)
         }
   $w tag configure id-$new -lmargin1 "[expr {13 * ([llength $taglist]-1) }]p"
   if { $parent != 0 && ![info exists tree($w,children,$parent)] } {
        setUpParent $w $parent
      }
   lappend tree($w,children,$parent) $new
   if { $parent == 0 } {
        set where end
      } else {
        if { [catch {$w index sub-$parent.last} where] } {
             set where [$w index id-$parent.last]
           }
      }
   $w insert $where " $txt\n" $taglist
   set where [$w index id-$new.first+1char]
   $w image create $where -image ::ttree::tree-dot -align center -pady 2 -padx 4
   $w tag add btn-$new $where
   if { $cmd != "" } {
        $w tag bind id-$new <1> $cmd
      }       
   return $new;
 };# ttree::addSub

 proc ::ttree::setUpParent {w parent} {
   variable tree;

   $w tag configure sub-$parent -elide 1 
   set tree($w,elide,$parent) 1
   $w tag lower btn-$parent
   $w tag lower sub-$parent 
   $w tag bind btn-$parent <Button-1> [list ::ttree::toggle $w $parent]
   $w image configure btn-$parent.first -image ::ttree::tree-open

 };# ttree::setUpParent

 proc ::ttree::toggle {w parent} {
   variable tree;

   set base [expr {!$tree($w,elide,$parent)}]
   set tree($w,elide,$parent) $base
   $w image configure btn-$parent.first -image [expr {$base ? "::ttree::tree-open" : "::ttree::tree-close"}]
   $w tag configure sub-$parent -elide [expr { $base ? 1 : "" }]

 };# ttree::toggle

 proc ::ttree::show {w id} {
   variable tree;

   while { [info exists tree($w,parent,$id)] } {
      set id $tree($w,parent,$id)
      if { $id == 0 } {
           break;
         }
      if { $tree($w,elide,$id) } {
           toggle $w $id
         }
   }
 };# ttree::show

 # Optional, export [tree] and [add] into the global namespace
 namespace eval ::ttree {namespace export tree add}
 namespace import ::ttree::*

        """
        from tkinter import _default_root
        _default_root.eval(MinimalTree)
        if master is None:
            master = _default_root
        super().__init__(master, "::ttree::tree")

    def add(self, parent: int = 0, text: int = "", command=_command):
        """
        添加列

        Attributes:
            parent(Widget): 列所在行
            text(int): 列文本
            command: 点击事件
        """
        from tkinter import _default_root
        command = _default_root.register(command)
        _default_root.call("::ttree::add", self, parent, text, command)

    def toggle(self, parent: Widget = 0):
        """
        切换。将收起的列展开

        Attributes:
            parent(Widget): 展开行
        """
        from tkinter import _default_root
        _default_root.call("::ttree::toggle", self, parent)

    def setup_parent(self, parent: Widget = 0):
        from tkinter import _default_root
        _default_root.call("::ttree::setUpParent", self, parent)

    def show(self, id: Widget = 0):
        from tkinter import _default_root
        _default_root.call("::ttree::show", self, id)

    def testtk(self):
        from tkinter import _default_root
        _default_root.eval("""
pack [ttree::tree .t]
ttree::add .t 0 Foo {puts "foo"}
ttree::add .t 0 Bar {puts "bar"}
ttree::add .t 1 Baz {}
ttree::add .t 1 Bleep {puts "bleep"}
ttree::add .t 0 Bloop {puts "bloop"}
ttree::add .t 0 Splash {puts "splash"}
ttree::add .t 3 Boing {puts "boing"}
ttree::add .t 3 Sprocket {puts "sprocket"}
ttree::add .t 3 Meep {puts "meep"}
""")

    def test(self):
        t = Tree()
        t.add(0, "Foo", lambda: print("foo"))
        t.add(0, "Bar", lambda: print("bar"))
        t.add(1, "Baz")
        t.add(1, "Bleep", lambda: print("bleep"))
        t.add(0, "Bloop", lambda: print("bloop"))
        t.add(0, "Splash", lambda: print("splash"))
        t.add(3, "Boing", lambda: print("boing"))
        t.add(3, "Sprocket", lambda: print("sprocked"))
        t.add(3, "Meep", lambda: print("meep"))
        t.pack()


if __name__ == '__main__':
    import tkinter as tk
    root = tk.Tk()
    ttree = Tree()
    ttree.test()
    root.mainloop()