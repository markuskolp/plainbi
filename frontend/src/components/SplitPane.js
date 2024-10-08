import React, {
    createRef,
    useContext,
    useEffect,
    useRef,
    useState,
  } from "react";
  import SplitPaneContext from "./SplitPaneContext";
  import "../css/splitpane.css";

  
  const SplitPane = ({ children, ...props }) => {
    const [clientHeight, setClientHeight] = useState(null);
    const [clientWidth, setClientWidth] = useState(null);
    const yDividerPos = useRef(null);
    const xDividerPos = useRef(null);
  
    const onMouseHoldDown = (e) => {
      yDividerPos.current = e.clientY;
      xDividerPos.current = e.clientX;
    };
  
    const onMouseHoldUp = () => {
      yDividerPos.current = null;
      xDividerPos.current = null;
    };
  
    const onMouseHoldMove = (e) => {
      if (!yDividerPos.current && !xDividerPos.current) {
        return;
      }
  
      setClientHeight(clientHeight + e.clientY - yDividerPos.current);
      setClientWidth(clientWidth + e.clientX - xDividerPos.current);
  
      yDividerPos.current = e.clientY;
      xDividerPos.current = e.clientX;
    };
  
    useEffect(() => {
      document.addEventListener("mouseup", onMouseHoldUp);
      document.addEventListener("mousemove", onMouseHoldMove);
  
      return () => {
        document.removeEventListener("mouseup", onMouseHoldUp);
        document.removeEventListener("mousemove", onMouseHoldMove);
      };
    });
  
    return (
      <div {...props}>
        <SplitPaneContext.Provider
          value={{
            clientHeight,
            setClientHeight,
            clientWidth,
            setClientWidth,
            onMouseHoldDown,
          }}
        >
          {children}
        </SplitPaneContext.Provider>
      </div>
    );
  };
  
  export const Divider = (props) => {
    const { onMouseHoldDown } = useContext(SplitPaneContext);
  
    return <div {...props} onMouseDown={onMouseHoldDown} />;
  };
  
  export const SplitPaneTop = (props) => {
    const topRef = createRef();
    const { clientHeight, setClientHeight } = useContext(SplitPaneContext);
  
    useEffect(() => {
      if (!clientHeight) {
        setClientHeight(topRef.current.clientHeight);
        return;
      }
  
      topRef.current.style.minHeight = clientHeight + "px";
      topRef.current.style.maxHeight = clientHeight + "px";
    }, [clientHeight]);
  
    return (
      <div {...props} className="split-pane-top" ref={topRef}>
        {children}
      </div>
    );
  };
  
  export const SplitPaneBottom = (props, children) => {
    const { currQuote } = useContext(QuoteContext);
  
    return (
      <div {...props} className="split-pane-bottom">
        {children}
      </div>
    );
  };
  
  export const SplitPaneLeft = (props) => {
    const topRef = createRef();
    const { clientWidth, setClientWidth } = useContext(SplitPaneContext);
  
    useEffect(() => {
      if (!clientWidth) {
        setClientWidth(topRef.current.clientWidth / 2);
        return;
      }
  
      topRef.current.style.minWidth = clientWidth + "px";
      topRef.current.style.maxWidth = clientWidth + "px";
    }, [clientWidth]);
  
    return <div {...props} className="split-pane-left" ref={topRef} />;
  };
  
  export const SplitPaneRight = (props, children) => {
    
    return (
      <div {...props} className="split-pane-right">
        {children}
      </div>
    );
  };
  
  export default SplitPane;