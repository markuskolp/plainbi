import React, { useState, useCallback } from 'react';
import { PageHeader } from "@ant-design/pro-layout";
import ReactFlow, {
  Controls,
  Background,
  applyNodeChanges,
  applyEdgeChanges,
  ReactFlowProvider 
} from 'reactflow';
import 'reactflow/dist/style.css';
import MonacoEditor from 'react-monaco-editor';
import "../css/erd.css";

/*
const ERD = () => {
  return (
  );
};
*/

const initialNodes = [
  {
    id: 'erstes ER Diagramm',
    data: { label: 'erstes ER Diagramm' },
    position: { x: 0, y: 0 },
    type: 'input',
  },
  {
    id: 'los gehts !',
    data: { label: 'los gehts !' },
    position: { x: 100, y: 100 },
  },
];

const initialEdges = [
  { id: '1-2', source: 'erstes ER Diagramm', target: 'los gehts !', label: '... na dann ...', type: 'step' },
];

//const ERDFlow = () => {
function ERD() {

  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [],
  );
  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [],
  );
  
  const handleMonacoEditorChange = (value,e) => {
    //const emuEvent = { "target": { "name": name, "value": value}} // emulate event.target.name/.value object
    //console.log(emuEvent);
    console.log("value: " + value);
    console.log("e: " + e);
  }
  
 const MonacoEditorOptions = {
    autoIndent: 'full',
    contextmenu: true,
    //fontFamily: 'monospace',
    //fontSize: 13,
    //lineHeight: 24,
    hideCursorInOverviewRuler: true,
    matchBrackets: 'always',
    minimap: {
      enabled: false,
    },
    scrollbar: {
      horizontalSliderSize: 2,
      verticalSliderSize: 10,
    },
    selectOnLineNumbers: true,
    roundedSelection: false,
    readOnly: false,
    cursorStyle: 'line',
    automaticLayout: true,
}; 

const defaultValue = 'Entity "erstes ER Diagramm"\nEntity "los gehts"\n\nRelation "erstes ER Diagramm" > "los gehts"';

  return (
    <React.Fragment>
      <PageHeader
              title="ER Diagramm"
              subTitle=""
            />
      <div class="erdcontainer">
        <div class="erdcontainer_editor">
          <MonacoEditor
                        width="100%"
                        height="100%"
                        language="sql"
                        theme="vs-light"
                        value={defaultValue}
                        options={MonacoEditorOptions}
                        //onChange={::this.onChange}
                        onChange={handleMonacoEditorChange}
                        name={name}
                        //editorDidMount={::this.editorDidMount}
                        />
        </div>
        <div class="erdcontainer_result" >
          <ReactFlow
            nodes={nodes}
            onNodesChange={onNodesChange}
            edges={edges}
            onEdgesChange={onEdgesChange}
            fitView
          >
            <Background />
            <Controls />
          </ReactFlow>
        </div>
      </div>
    </React.Fragment>
  );
}


export default ERD;

/*
    <div style={{ width: '100%', height: '100%' }}>
    <div style={{ width: '100vw', height: '100vh' }}>
<div style={{ height: '100%' }}>
    <ReactFlowProvider>
    

    
function ERD(props) {
  return (
    <ReactFlowProvider>
      <ERDFlow {...props} />
    </ReactFlowProvider>
  );
}
    */