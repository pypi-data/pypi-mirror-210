from dash import html, dcc


class Button(html.Div):
    """
    A Button component.
    Button is a wrapper for the <button> HTML5 element.
    For detailed attribute info see:
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button

    Keyword arguments:

    - children (a list of or a singular dash component, string or number; optional):
        The children of this component.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all the components
        in an app.

    - accessKey (string; optional):
        Keyboard shortcut to activate or add focus to the element.

    - aria-* (string; optional):
        A wildcard aria attribute.

    - autoFocus (a value equal to: 'autoFocus', 'autofocus', 'AUTOFOCUS' | boolean; optional):
        The element should be automatically focused after the page loaded.

    - className (string; optional):
        Often used with CSS to style elements with common properties.

    - contentEditable (string; optional):
        Indicates whether the element's content is editable.

    - contextMenu (string; optional):
        Defines the ID of a <menu> element which will serve as the
        element's context menu.

    - data-* (string; optional):
        A wildcard data attribute.

    - dir (string; optional):
        Defines the text direction. Allowed values are ltr (Left-To-Right)
        or rtl (Right-To-Left).

    - disable_n_clicks (boolean; optional):
        When True, this will disable the n_clicks prop.  Use this to
        remove event listeners that may interfere with screen readers.

    - disabled (a value equal to: 'disabled', 'DISABLED' | boolean; optional):
        Indicates whether the user can interact with the element.

    - draggable (string; optional):
        Defines whether the element can be dragged.

    - form (string; optional):
        Indicates the form that is the owner of the element.

    - formAction (string; optional):
        Indicates the action of the element, overriding the action defined
        in the <form>.

    - formEncType (string; optional):
        If the button/input is a submit button (e.g. type=\"submit\"),
        this attribute sets the encoding type to use during form
        submission. If this attribute is specified, it overrides the
        enctype attribute of the button's form owner.

    - formMethod (string; optional):
        If the button/input is a submit button (e.g. type=\"submit\"),
        this attribute sets the submission method to use during form
        submission (GET, POST, etc.). If this attribute is specified, it
        overrides the method attribute of the button's form owner.

    - formNoValidate (a value equal to: 'formNoValidate', 'formnovalidate', 'FORMNOVALIDATE' | boolean; optional):
        If the button/input is a submit button (e.g. type=\"submit\"),
        this boolean attribute specifies that the form is not to be
        validated when it is submitted. If this attribute is specified, it
        overrides the novalidate attribute of the button's form owner.

    - formTarget (string; optional):
        If the button/input is a submit button (e.g. type=\"submit\"),
        this attribute specifies the browsing context (for example, tab,
        window, or inline frame) in which to display the response that is
        received after submitting the form. If this attribute is
        specified, it overrides the target attribute of the button's form
        owner.

    - hidden (a value equal to: 'hidden', 'HIDDEN' | boolean; optional):
        Prevents rendering of given element, while keeping child elements,
        e.g. script elements, active.

    - key (string; optional):
        A unique identifier for the component, used to improve performance
        by React.js while rendering components See
        https://reactjs.org/docs/lists-and-keys.html for more info.

    - lang (string; optional):
        Defines the language used in the element.

    - loading_state (dict; optional):
        Object that holds the loading state object coming from
        dash-renderer.

        `loading_state` is a dict with keys:

        - component_name (string; optional):
            Holds the name of the component that is loading.

        - is_loading (boolean; optional):
            Determines if the component is loading or not.

        - prop_name (string; optional):
            Holds which property is loading.

    - n_clicks (number; default 0):
        An integer that represents the number of times that this element
        has been clicked on.

    - n_clicks_timestamp (number; default -1):
        An integer that represents the time (in ms since 1970) at which
        n_clicks changed. This can be used to tell which button was
        changed most recently.

    - name (string; optional):
        Name of the element. For example used by the server to identify
        the fields in form submits.

    - role (string; optional):
        Defines an explicit role for an element for use by assistive
        technologies.

    - spellCheck (string; optional):
        Indicates whether spell checking is allowed for the element.

    - style (dict; optional):
        Defines CSS styles which will override styles previously set.

    - tabIndex (string; optional):
        Overrides the browser's default tab order and follows the one
        specified instead.

    - title (string; optional):
        Text to be displayed in a tooltip when hovering over the element.

    - type (string; optional):
        Defines the type of the element.

    - value (string; optional):
        Defines a default value which will be displayed in the element on
        page load.
        """

    def __init__(self, **button_props):
        button_props = button_props.copy() if button_props else {}
        if 'style' not in button_props:
            button_props['style'] = {'border': 'none', 'padding': '12px 40px 12px 40px', 'border-radius': '24px',
                                     'background': '#0000C9', 'width': '136px', 'height': '48px',
                                     'font-family': 'Inter', 'color': '#ffffff'}
        super(Button, self).__init__(html.Button(**button_props))


class Checkbox(html.Div):
    """A Checklist component.
    Checklist is a component that encapsulates several checkboxes.
    The values and labels of the checklist are specified in the `options`
    property and the checked items are specified with the `value` property.
    Each checkbox is rendered as an input with a surrounding label.

    Keyword arguments:

    - options (list of dicts; optional):
        An array of options.

        `options` is a list of string | number | booleans | dict | list of
        dicts with keys:

        - disabled (boolean; optional):
            If True, this option is disabled and cannot be selected.

        - label (a list of or a singular dash component, string or number; required):
            The option's label.

        - title (string; optional):
            The HTML 'title' attribute for the option. Allows for
            information on hover. For more information on this attribute,
            see
            https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/title.

        - value (string | number | boolean; required):
            The value of the option. This value corresponds to the items
            specified in the `value` property.

    - value (list of string | number | booleans; optional):
        The currently selected value.

    - inline (boolean; default False):
        Indicates whether the options labels should be displayed inline
        (True=horizontal) or in a block (False=vertical).

    - className (string; optional):
        The class of the container (div).

    - style (dict; optional):
        The style of the container (div).

    - inputStyle (dict; optional):
        The style of the <input> checkbox element.

    - inputClassName (string; default ''):
        The class of the <input> checkbox element.

    - labelStyle (dict; optional):
        The style of the <label> that wraps the checkbox input  and the
        option's label.

    - labelClassName (string; default ''):
        The class of the <label> that wraps the checkbox input  and the
        option's label.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all the components
        in an app.

    - loading_state (dict; optional):
        Object that holds the loading state object coming from
        dash-renderer.

        `loading_state` is a dict with keys:

        - component_name (string; optional):
            Holds the name of the component that is loading.

        - is_loading (boolean; optional):
            Determines if the component is loading or not.

        - prop_name (string; optional):
            Holds which property is loading.

    - persistence (boolean | string | number; optional):
        Used to allow user interactions in this component to be persisted
        when the component - or the page - is refreshed. If `persisted` is
        truthy and hasn't changed from its previous value, a `value` that
        the user has changed while using the app will keep that change, as
        long as the new `value` also matches what was given originally.
        Used in conjunction with `persistence_type`.

    - persisted_props (list of a value equal to: 'value's; default ['value']):
        Properties whose user interactions will persist after refreshing
        the component or the page. Since only `value` is allowed this prop
        can normally be ignored.

    - persistence_type (a value equal to: 'local', 'session', 'memory'; default 'local'):
        Where persisted user changes will be stored: memory: only kept in
        memory, reset on page refresh. local: window.localStorage, data is
        kept after the browser quit. session: window.sessionStorage, data
        is cleared once the browser quit."""

    def __init__(self, checklist_props=None):
        checklist_props = checklist_props.copy() if checklist_props else {}
        if "style" not in checklist_props:
            checklist_props['style'] = {"display": "flex", "flex-direction": "column"}
        super(Checkbox, self).__init__(dcc.Checklist(**checklist_props))


class Dropdown(html.Div):
    """A Dropdown component.
    Dropdown is an interactive dropdown element for selecting one or more
    items.
    The values and labels of the dropdown items are specified in the `options`
    property and the selected item(s) are specified with the `value` property.

    Use a dropdown when you have many options (more than 5) or when you are
    constrained for space. Otherwise, you can use RadioItems or a Checklist,
    which have the benefit of showing the users all the items at once.

    Keyword arguments:

    - options (list of dicts; optional):
        An array of options {label: [string|number], value:
        [string|number]}, an optional disabled field can be used for each
        option.

        `options` is a list of string | number | booleans | dict | list of
        dicts with keys:

        - disabled (boolean; optional):
            If True, this option is disabled and cannot be selected.

        - label (a list of or a singular dash component, string or number; required):
            The option's label.

        - search (string; optional):
            Optional search value for the option, to use if the label is a
            component or provide a custom search value different from the
            label. If no search value and the label is a component, the
            `value` will be used for search.

        - title (string; optional):
            The HTML 'title' attribute for the option. Allows for
            information on hover. For more information on this attribute,
            see
            https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/title.

        - value (string | number | boolean; required):
            The value of the option. This value corresponds to the items
            specified in the `value` property.

    - value (string | number | boolean | list of string | number | booleans; optional):
        The value of the input. If `multi` is False (the default) then
        value is just a string that corresponds to the values provided in
        the `options` property. If `multi` is True, then multiple values
        can be selected at once, and `value` is an array of items with
        values corresponding to those in the `options` prop.

    - multi (boolean; default False):
        If True, the user can select multiple values.

    - clearable (boolean; default True):
        Whether the dropdown is \"clearable\", that is, whether
        a small \"x\" appears on the right of the dropdown that
        removes the selected value.

    - searchable (boolean; default True):
        Whether to enable the searching feature or not.

    - search_value (string; optional):
        The value typed in the DropDown for searching.

    - placeholder (string; optional):
        The grey, default text shown when no option is selected.

    - disabled (boolean; default False):
        If True, this dropdown is disabled and the selection cannot be
        changed.

    - optionHeight (number; default 35):
        height of each option. Can be increased when label lengths would
        wrap around.

    - maxHeight (number; default 200):
        height of the options dropdown.

    - style (dict; optional):
        Defines CSS styles which will override styles previously set.

    - className (string; optional):
        className of the dropdown element.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all the components
        in an app.

    - loading_state (dict; optional):
        Object that holds the loading state object coming from
        dash-renderer.

        `loading_state` is a dict with keys:

        - component_name (string; optional):
            Holds the name of the component that is loading.

        - is_loading (boolean; optional):
            Determines if the component is loading or not.

        - prop_name (string; optional):
            Holds which property is loading.

    - persistence (boolean | string | number; optional):
        Used to allow user interactions in this component to be persisted
        when the component - or the page - is refreshed. If `persisted` is
        truthy and hasn't changed from its previous value, a `value` that
        the user has changed while using the app will keep that change, as
        long as the new `value` also matches what was given originally.
        Used in conjunction with `persistence_type`.

    - persisted_props (list of a value equal to: 'value's; default ['value']):
        Properties whose user interactions will persist after refreshing
        the component or the page. Since only `value` is allowed this prop
        can normally be ignored.

    - persistence_type (a value equal to: 'local', 'session', 'memory'; default 'local'):
        Where persisted user changes will be stored: memory: only kept in
        memory, reset on page refresh. local: window.localStorage, data is
        kept after the browser quit. session: window.sessionStorage, data
        is cleared once the browser quit."""

    def __init__(self, dropdown_props=None):
        dropdown_props = dropdown_props.copy() if dropdown_props else {}
        if 'style' not in dropdown_props:
            dropdown_props['style'] = {'position': 'relative',
                                       'border': '1px dashed #7B61FF',
                                       'border-radius': 5,
                                       'box-sizing': 'border-box',
                                       }
        super(Dropdown, self).__init__(dcc.Dropdown(**dropdown_props))


class Input(html.Div):
    """An Input component.
    A basic HTML input control for entering text, numbers, or passwords.

    Note that checkbox and radio types are supported through
    the Checklist and RadioItems component. Dates, times, and file uploads
    are also supported through separate components.

    Keyword arguments:

    - value (string | number; optional):
        The value of the input.

    - type (a value equal to: 'text', 'number', 'password', 'email', 'range', 'search', 'tel', 'url', 'hidden'; default 'text'):
        The type of control to render.

    - debounce (boolean; default False):
        If True, changes to input will be sent back to the Dash server
        only on enter or when losing focus. If it's False, it will sent
        the value back on every change.

    - placeholder (string | number; optional):
        A hint to the user of what can be entered in the control . The
        placeholder text must not contain carriage returns or line-feeds.
        Note: Do not use the placeholder attribute instead of a <label>
        element, their purposes are different. The <label> attribute
        describes the role of the form element (i.e. it indicates what
        kind of information is expected), and the placeholder attribute is
        a hint about the format that the content should take. There are
        cases in which the placeholder attribute is never displayed to the
        user, so the form must be understandable without it.

    - n_submit (number; default 0):
        Number of times the `Enter` key was pressed while the input had
        focus.

    - n_submit_timestamp (number; default -1):
        Last time that `Enter` was pressed.

    - inputMode (a value equal to: 'verbatim', 'latin', 'latin-name', 'latin-prose', 'full-width-latin', 'kana', 'katakana', 'numeric', 'tel', 'email', 'url'; optional):
        Provides a hint to the browser as to the type of data that might
        be entered by the user while editing the element or its contents.

    - autoComplete (string; optional):
        This attribute indicates whether the value of the control can be
        automatically completed by the browser.

    - readOnly (boolean | a value equal to: 'readOnly', 'readonly', 'READONLY'; optional):
        This attribute indicates that the user cannot modify the value of
        the control. The value of the attribute is irrelevant. If you need
        read-write access to the input value, do not add the \"readonly\"
        attribute. It is ignored if the value of the type attribute is
        hidden, range, color, checkbox, radio, file, or a button type
        (such as button or submit). readOnly is an HTML boolean attribute
        - it is enabled by a boolean or 'readOnly'. Alternative
        capitalizations `readonly` & `READONLY` are also acccepted.

    - required (a value equal to: 'required', 'REQUIRED' | boolean; optional):
        This attribute specifies that the user must fill in a value before
        submitting a form. It cannot be used when the type attribute is
        hidden, image, or a button type (submit, reset, or button). The
        :optional and :required CSS pseudo-classes will be applied to the
        field as appropriate. required is an HTML boolean attribute - it
        is enabled by a boolean or 'required'. Alternative capitalizations
        `REQUIRED` are also acccepted.

    - autoFocus (a value equal to: 'autoFocus', 'autofocus', 'AUTOFOCUS' | boolean; optional):
        The element should be automatically focused after the page loaded.
        autoFocus is an HTML boolean attribute - it is enabled by a
        boolean or 'autoFocus'. Alternative capitalizations `autofocus` &
        `AUTOFOCUS` are also acccepted.

    - disabled (a value equal to: 'disabled', 'DISABLED' | boolean; optional):
        If True, the input is disabled and can't be clicked on. disabled
        is an HTML boolean attribute - it is enabled by a boolean or
        'disabled'. Alternative capitalizations `DISABLED`.

    - list (string; optional):
        Identifies a list of pre-defined options to suggest to the user.
        The value must be the id of a <datalist> element in the same
        document. The browser displays only options that are valid values
        for this input element. This attribute is ignored when the type
        attribute's value is hidden, checkbox, radio, file, or a button
        type.

    - multiple (boolean; optional):
        This Boolean attribute indicates whether the user can enter more
        than one value. This attribute applies when the type attribute is
        set to email or file, otherwise it is ignored.

    - spellCheck (a value equal to: 'true', 'false' | boolean; optional):
        Setting the value of this attribute to True indicates that the
        element needs to have its spelling and grammar checked. The value
        default indicates that the element is to act according to a
        default behavior, possibly based on the parent element's own
        spellcheck value. The value False indicates that the element
        should not be checked.

    - name (string; optional):
        The name of the control, which is submitted with the form data.

    - min (string | number; optional):
        The minimum (numeric or date-time) value for this item, which must
        not be greater than its maximum (max attribute) value.

    - max (string | number; optional):
        The maximum (numeric or date-time) value for this item, which must
        not be less than its minimum (min attribute) value.

    - step (string | number; default 'any'):
        Works with the min and max attributes to limit the increments at
        which a numeric or date-time value can be set. It can be the
        string any or a positive floating point number. If this attribute
        is not set to any, the control accepts only values at multiples of
        the step value greater than the minimum.

    - minLength (string | number; optional):
        If the value of the type attribute is text, email, search,
        password, tel, or url, this attribute specifies the minimum number
        of characters (in Unicode code points) that the user can enter.
        For other control types, it is ignored.

    - maxLength (string | number; optional):
        If the value of the type attribute is text, email, search,
        password, tel, or url, this attribute specifies the maximum number
        of characters (in UTF-16 code units) that the user can enter. For
        other control types, it is ignored. It can exceed the value of the
        size attribute. If it is not specified, the user can enter an
        unlimited number of characters. Specifying a negative number
        results in the default behavior (i.e. the user can enter an
        unlimited number of characters). The constraint is evaluated only
        when the value of the attribute has been changed.

    - pattern (string; optional):
        A regular expression that the control's value is checked against.
        The pattern must match the entire value, not just some subset. Use
        the title attribute to describe the pattern to help the user. This
        attribute applies when the value of the type attribute is text,
        search, tel, url, email, or password, otherwise it is ignored. The
        regular expression language is the same as JavaScript RegExp
        algorithm, with the 'u' parameter that makes it treat the pattern
        as a sequence of unicode code points. The pattern is not
        surrounded by forward slashes.

    - selectionStart (string; optional):
        The offset into the element's text content of the first selected
        character. If there's no selection, this value indicates the
        offset to the character following the current text input cursor
        position (that is, the position the next character typed would
        occupy).

    - selectionEnd (string; optional):
        The offset into the element's text content of the last selected
        character. If there's no selection, this value indicates the
        offset to the character following the current text input cursor
        position (that is, the position the next character typed would
        occupy).

    - selectionDirection (string; optional):
        The direction in which selection occurred. This is \"forward\" if
        the selection was made from left-to-right in an LTR locale or
        right-to-left in an RTL locale, or \"backward\" if the selection
        was made in the opposite direction. On platforms on which it's
        possible this value isn't known, the value can be \"none\"; for
        example, on macOS, the default direction is \"none\", then as the
        user begins to modify the selection using the keyboard, this will
        change to reflect the direction in which the selection is
        expanding.

    - n_blur (number; default 0):
        Number of times the input lost focus.

    - n_blur_timestamp (number; default -1):
        Last time the input lost focus.

    - size (string; optional):
        The initial size of the control. This value is in pixels unless
        the value of the type attribute is text or password, in which case
        it is an integer number of characters. Starting in, this attribute
        applies only when the type attribute is set to text, search, tel,
        url, email, or password, otherwise it is ignored. In addition, the
        size must be greater than zero. If you do not specify a size, a
        default value of 20 is used.' simply states \"the user agent
        should ensure that at least that many characters are visible\",
        but different characters can have different widths in certain
        fonts. In some browsers, a certain string with x characters will
        not be entirely visible even if size is defined to at least x.

    - style (dict; optional):
        The input's inline styles.

    - className (string; optional):
        The class of the input element.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - loading_state (dict; optional):
        Object that holds the loading state object coming from
        dash-renderer.

        `loading_state` is a dict with keys:

        - component_name (string; optional):
            Holds the name of the component that is loading.

        - is_loading (boolean; optional):
            Determines if the component is loading or not.

        - prop_name (string; optional):
            Holds which property is loading.

    - persistence (boolean | string | number; optional):
        Used to allow user interactions in this component to be persisted
        when the component - or the page - is refreshed. If `persisted` is
        truthy and hasn't changed from its previous value, a `value` that
        the user has changed while using the app will keep that change, as
        long as the new `value` also matches what was given originally.
        Used in conjunction with `persistence_type`.

    - persisted_props (list of a value equal to: 'value's; default ['value']):
        Properties whose user interactions will persist after refreshing
        the component or the page. Since only `value` is allowed this prop
        can normally be ignored.

    - persistence_type (a value equal to: 'local', 'session', 'memory'; default 'local'):
        Where persisted user changes will be stored: memory: only kept in
        memory, reset on page refresh. local: window.localStorage, data is
        kept after the browser quit. session: window.sessionStorage, data
        is cleared once the browser quit."""

    def __init__(self, input_props=None):
        input_props = input_props.copy() if input_props else {}
        if 'style' not in input_props:
            input_props['style'] = {'position': 'relative',
                                    'border': '1px dashed #7B61FF',
                                    'border-radius': 5,
                                    'box-sizing': 'border-box'
                                    }
        super(Input, self).__init__(dcc.Input(**input_props))
