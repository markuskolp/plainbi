import React, { useState, useCallback } from 'react';
import { PageHeader } from "@ant-design/pro-layout";
import { Col, Row, Divider } from 'antd';
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
//import Split from 'react-split';

/*import SplitPane, {
  Divider,
  SplitPaneBottom,
  SplitPaneLeft,
  SplitPaneRight,
  SplitPaneTop,
} from "../components/SplitPane";
*/

/*
const ERD = () => {
  return (
  );
};
*/

const initialNodes = [
  {
    id: 'a',
    data: { label: 'erstes ER Diagramm' },
    position: { x: 0, y: 0 },
    //type: 'input',
  },
  {
    id: 'b',
    data: { label: 'los gehts !' },
    position: { x: 100, y: 100 },
  },
];

const initialEdges = [
  { id: 'a-b', source: 'a', target: 'b', label: '... na dann ...', type: 'step' },
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

  const defaultValue = 'a: erstes ER Diagramm\nb: los gehts\n\na > b';

  /* splitpane function - START */

  let ismdwn = 0

  function mD(event) {
    ismdwn = 1
    document.body.addEventListener('mousemove', mV)
    document.body.addEventListener('mouseup', end)
    console.log("mD")
  }

  function mV(event) {
    console.log("mV")
    if (ismdwn === 1) {
      pan1.style.flex = event.clientX + "px"
    } else {
      end()
    }
  }
  const end = (e) => {
    ismdwn = 0
    document.body.removeEventListener('mouseup', end)
    document.getElementById('rpanrResize').removeEventListener('mousemove', mV)
  }

  function rC(event) {
    document.getElementById('rpanrResize').addEventListener('mousedown', mD)
  }
  /* splitpane function - END */


  // https://github.com/nerdify/dbml-parser/blob/master/index.js

  const parseDSLtoFlow = (text) => {
    try {

      //cleanse DSL text
      let dsltext = text;
      dsltext = dsltext.replace(/\/\*[\s\S]*?\*\/|(?<=[^:])\/\/.*|^\/\/.*/g, '').trim(); // removeComments
      dsltext = dsltext.split(/\r?\n/).filter(line => line.trim() !== '').join('\n'); // trimEmptyLines
      console.log(dsltext);

      let flow = {
          nodes: dsltext.split("\n").filter(line => line.split(":").length > 1 ).map((line, i) => {  // nur nodes nehmen (durch : getrennt)
            return  {  
                id: line.split(":")[0].trim(),
                label: line.split(":")[1].trim(),
                layout: {x: 0, y: i*100}
            }
          }),
          edges: dsltext.split("\n").filter(line => line.split(">").length > 1 ).map((line, i) => {  // nur nodes nehmen (durch : getrennt)
            return  {  
                id: line.split(">")[0].trim() + "-"+ line.split(":")[1],
                from: line.split(">")[0].trim(),
                to: line.split(">")[1].trim(),
                label: null, //line.split(":")[1],
                type: 'smoothstep' // https://reactflow.dev/examples/edges/edge-types
            }
          })

      };
      console.log(flow);

      return flow; 
    } catch (error) {
      console.error(error);
      return null;
    }
  };


  const handleMonacoEditorChange = (value, e) => {
    try {
      //const emuEvent = { "target": { "name": name, "value": value}} // emulate event.target.name/.value object
      //console.log(emuEvent);
      console.log("value: " + value);
      console.log("e: " + e);

      const flow = parseDSLtoFlow(value);
    
      const newNodes = flow.nodes.map((node) => {
        
        let existingNode = nodes.find((existingnode) => existingnode.id == node.id);
        console.log("node - id: " + node.id);
        console.log(existingNode);

        return {
          id: node.id.toString(),
          position: { 
            x: (existingNode == null ? node.layout.x : existingNode.position.x ), 
            y: (existingNode == null ? node.layout.y : existingNode.position.y )
          },
          data: { label: node.label },
        };
      });
      
      const newEdges = flow.edges.map((edge) => ({
        id: edge.id.toString(),
        source: edge.from.toString(),
        target: edge.to.toString(),
        label: edge.label, //.toString()
        type: edge.type
      }));
      

      setNodes(newNodes);
      setEdges(newEdges);

    } catch (error) {
      //showModal('Error parsing HJson: ' + error);
      console.error(error);
    }

  }



return (
  <React.Fragment>
    <PageHeader className="erdheader" title="ER Diagramm" subTitle="" />

    <Row className="erdcontainer">
      <Col flex="20%" className="erdcontainer_editor">
        <MonacoEditor
          width="100%"
          height="80vh"
          language="sql"
          theme="vs-light"
          value={defaultValue}
          options={MonacoEditorOptions}
          //onChange={::this.onChange}
          onChange={handleMonacoEditorChange}
          name={name}
        //editorDidMount={::this.editorDidMount}
        />
      </Col>
      <Col flex="20px">
        <Divider type="vertical" style={{ height: "100%", borderWidth: "thick" }} />
      </Col>
      <Col flex="auto" className="erdcontainer_result" >
        <ReactFlow
          nodes={nodes}
          onNodesChange={onNodesChange}
          edges={edges}
          onEdgesChange={onEdgesChange}
          fitView
        >
          <Background color="#fff" />
          <Controls position="bottom-right" />
        </ReactFlow>
      </Col>
    </Row>
  </React.Fragment>
);
}


export default ERD;

/*


      <Row className="erdcontainer">
        <Col id="pan1" >
            <MonacoEditor
                          width="100%"
                          height="80vh"
                          language="sql"
                          theme="vs-light"
                          value={defaultValue}
                          options={MonacoEditorOptions}
                          //onChange={::this.onChange}
                          onChange={handleMonacoEditorChange}
                          name={name}
                          //editorDidMount={::this.editorDidMount}
                          />
        </Col>
        <Col id="rpanrResize" onClick={rC}>
          <Divider type="vertical" style={{ height: "100%", borderWidth: "thick" }} />
        </Col>
        <Col id="pan2" >
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
      </Col>
    </Row>

        <SplitPane className="split-pane-row">
          <SplitPaneLeft>
          </SplitPaneLeft>
          <Divider className="separator-col" />
          <SplitPaneRight>
          </SplitPaneRight>
        </SplitPane>

      <Row class="erdcontainer">
      <Col flex="300px" class="erdcontainer_editor">
          <MonacoEditor
                        width="100%"
                        height="80vh"
                        language="sql"
                        theme="vs-light"
                        value={defaultValue}
                        options={MonacoEditorOptions}
                        //onChange={::this.onChange}
                        onChange={handleMonacoEditorChange}
                        name={name}
                        //editorDidMount={::this.editorDidMount}
                        />
      </Col>
      <Col flex="20px">
        <Divider type="vertical" style={{ height: "100%", borderWidth: "thick" }} />
      </Col>
      <Col flex="auto" class="erdcontainer_result" >
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
      </Col>
    </Row>

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


    <Row>
      <Col span={11}>
        CONTENT ONE SIDE
        <br />
        CONTENT ONE SIDE
        <br />
        CONTENT ONE SIDE
        <br />
      </Col>
      <Col span={2}>
        <Divider type="vertical" style={{ height: "100%" }} />
      </Col>
      <Col span={11}>CONTENT OTHER SIDE</Col>
    </Row>
    */