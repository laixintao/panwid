import logging
logger = logging.getLogger("urwid_datatable")

import urwid

intersperse = lambda e,l: sum([[x, e] for x in l],[])[:-1]

class DataTableCell(urwid.WidgetWrap):

    signals = ["click", "select"]

    ATTR = "table_cell"
    PADDING_ATTR = "table_row_padding"

    def __init__(self, table, column,
                 value=None, value_attr=None,
                 padding=0,
                 *args, **kwargs):


        self.table = table
        self.attr = self.ATTR
        self.attr_focused = "%s focused" %(self.attr)
        self.attr_column_focused = "%s column_focused" %(self.attr)
        self.attr_highlight = "%s highlight" %(self.attr)
        self.attr_highlight_focused = "%s focused" %(self.attr_highlight)
        self.attr_highlight_column_focused = "%s column_focused" %(self.attr_highlight)

        self.column = column
        self.value = value
        self.value_attr = value_attr

        if column.padding:
            self.padding = column.padding
        else:
            self.padding = padding

        self.contents = self._format(value)

        self.padding = urwid.Padding(
            self.contents,
            left=self.padding,
            right=self.padding
        )

        self.normal_attr_map = {}
        self.highlight_attr_map = {}

        self.normal_focus_map = {}
        self.highlight_focus_map = {}

        self.set_attr_maps()

        self.highlight_attr_map.update(self.table.highlight_map)
        self.highlight_focus_map.update(self.table.highlight_focus_map)

        self.attr = urwid.AttrMap(
            self.padding,
            attr_map = self.normal_attr_map,
            focus_map = self.normal_focus_map
        )
        super(DataTableCell, self).__init__(self.attr)

    def set_attr_maps(self):

        self.normal_attr_map[None] = self.attr
        self.highlight_attr_map [None] = self.attr_highlight
        self.normal_focus_map[None] = self.attr_focused
        self.highlight_focus_map[None] = self.attr_highlight

        if self.value_attr:
            self.normal_attr_map.update({None: self.value_attr})
            self.normal_focus_map.update({None: "%s focused" %(self.value_attr)})
            self.highlight_attr_map.update({None: "%s highlight" %(self.value_attr)})
            self.highlight_focus_map.update({None: "%s highlight focused" %(self.value_attr)})


    def highlight(self):
        self.attr.set_attr_map(self.highlight_attr_map)
        self.attr.set_focus_map(self.highlight_focus_map)


    def unhighlight(self):
        self.attr.set_attr_map(self.normal_attr_map)
        self.attr.set_focus_map(self.normal_focus_map)

    def selectable(self):
        return False

    def keypress(self, size, key):
        return key
        # return super(DataTableCell, self).keypress(size, key)

    def _format(self, v):
        return self.column._format(v)

    def set_attr_map(self, attr_map):
        self.attr.set_attr_map(attr_map)

    def mouse_event(self, size, event, button, col, row, focus):
        if event == 'mouse press':
            urwid.emit_signal(self, "click")


class DataTableBodyCell(DataTableCell):
    ATTR = "table_row_body"
    PADDING_ATTR = "table_row_body_padding"



class DataTableHeaderCell(DataTableCell):
    ATTR = "table_row_header"
    PADDING_ATTR = "table_row_header_padding"

    ASCENDING_SORT_MARKER = u"\N{UPWARDS ARROW}"
    DESCENDING_SORT_MARKER = u"\N{DOWNWARDS ARROW}"

    def __init__(self, table, column, sort=None, sort_icon=None, *args, **kwargs):
        self.table = table
        self.column = column
        if self.column.sort_icon is not None:
            self.sort_icon = self.column.sort_icon
        else:
            self.sort_icon = sort_icon
        self.columns = urwid.Columns([
            ('weight', 1, urwid.Text(column.label, align=self.column.align))
        ])
        if sort_icon:
            self.columns.contents.append(
                (urwid.Text(""), self.columns.options("given", 1))
            )
        super(DataTableHeaderCell, self).__init__(self.table, column, self.columns, *args, **kwargs)
        self.update_sort(sort)

    def set_attr_maps(self):

        self.normal_attr_map[None] = self.attr
        self.highlight_attr_map [None] = self.attr_highlight
        self.normal_focus_map[None] = self.attr_column_focused
        self.highlight_focus_map[None] = self.attr_highlight_column_focused


    def _format(self, v):
        return self.column.format(v)

    def selectable(self):
        return self.table.ui_sort

    def keypress(self, size, key):
        if key != "enter":
            return key
        urwid.emit_signal(self, "select", self)

    def mouse_event(self, size, event, button, col, row, focus):
        if event == 'mouse press':
            urwid.emit_signal(self, "click", self)

    def update_sort(self, sort):
        if not self.sort_icon: return

        if sort and sort[0] == self.column.name:
            direction = self.DESCENDING_SORT_MARKER if sort[1] else self.ASCENDING_SORT_MARKER
            self.columns.contents[1][0].set_text(direction)
        else:
            self.columns.contents[1][0].set_text("")

class DataTableFooterCell(DataTableCell):
    ATTR = "table_row_footer"
    PADDING_ATTR = "table_row_footer_padding"
