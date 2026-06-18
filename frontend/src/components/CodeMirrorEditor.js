import CodeMirror from '@uiw/react-codemirror';
import { json } from '@codemirror/lang-json';
import { sql } from '@codemirror/lang-sql';
import { EditorView } from '@codemirror/view';

const editorTheme = EditorView.theme({
  '&': { backgroundColor: '#fff' },
  '.cm-content': { fontFamily: '"Consolas","Menlo","Monaco","Courier New",monospace !important', fontSize: '14px', padding: '2px 0' },
  '.cm-line': { padding: '0 6px' },
  '.cm-gutters': { backgroundColor: '#f8f8f8', borderRight: '1px solid #e8e8e8', color: '#aaa' },
  '.cm-activeLineGutter': { backgroundColor: '#e8f0ff' },
  '.cm-activeLine': { backgroundColor: '#f5f8ff' },
  '.cm-focused': { outline: 'none' },
  '.cm-editor': { height: '100%' },
  '.cm-scroller': { overflow: 'auto' },
  '&.cm-focused .cm-selectionBackground, .cm-selectionBackground': { backgroundColor: '#b3d4ff !important' },
  '.cm-cursor': { borderLeftColor: '#333' },
});

const readOnlyExt = [EditorView.editable.of(false)];

const CodeMirrorEditor = ({ value, onChange, language, readOnly, height = 300 }) => {
  const extensions = [
    language === 'json' ? json() : sql(),
    editorTheme,
    ...(readOnly ? readOnlyExt : []),
  ];

  return (
    <CodeMirror
      value={value ?? ''}
      height={typeof height === 'number' ? `${height}px` : height}
      extensions={extensions}
      onChange={readOnly ? undefined : onChange}
      basicSetup={{
        lineNumbers: true,
        highlightActiveLine: !readOnly,
        highlightActiveLineGutter: !readOnly,
        foldGutter: false,
        dropCursor: false,
        allowMultipleSelections: false,
        indentOnInput: true,
        bracketMatching: true,
        closeBrackets: !readOnly,
        autocompletion: false,
        rectangularSelection: false,
        crosshairCursor: false,
        highlightSelectionMatches: false,
      }}
    />
  );
};

export default CodeMirrorEditor;
