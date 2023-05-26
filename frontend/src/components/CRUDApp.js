import React from "react";
import { useState, useEffect } from "react";
import { Layout,  Menu} from "antd";
const { Header, Content, Sider } = Layout;
import CRUDPage from "./CRUDPage";

// TODO: make page switch work !

const CRUDApp = ({ name, pages, token }) => {
  
    const [selectedPage, setSelectedPage] = useState(1); // nr of selected page
    const [page, setPage] = useState(); // page metadata
    const [pageList, setPageList] = useState(); // page metadata

    useEffect(() => {
      setPage(pages[selectedPage-1]);
      setPageList(pages.map((page) => {
          console.log("CRUD / pages: " + page.name + ' - ' + page.id);
          return getItem(page.name, page.id);
        })
      );  
    }, []);

    // Layout settings
    const [mode, setMode] = useState("inline");
    const [theme, setTheme] = useState("light");

    // Switch page
    const switchPage = (e) => {
      const pageIndex = e.key - 1;
      console.log('switchPage() - set page to id: ' + e.key + ' = pageIndex: ' + pageIndex);
      setSelectedPage(e.key);
      setPage(pages[pageIndex]);
    };

    // return a item to be rendered in a Menu component
    function getItem(label, key, icon, children, type) {
      return {
        key,
        icon,
        children,
        label,
        type
      };
    }

    function getLookups(table_columns) {
      const lookups = table_columns.filter((column) => column.ui === "lookup").map((column) => ( 
          column.lookup
        )
      );
      console.log("getLookups: " + lookups);
      return lookups;
    };

    return (
    <Layout className="layout">
        <Header className="pageheader">{name}</Header>
        <Layout>
          {pages.length > 1 && // show only the sider menu (page list) when more than 1 page is listed
          <Sider width={250} theme={theme}>
            <Menu
              style={{ width: 250, marginTop: "25px" }}
              defaultSelectedKeys={["1"]}
              defaultOpenKeys={["1"]}
              mode={mode}
              theme={theme}
              items={pageList}
              onClick={switchPage}
            />
          </Sider>
          }
          { page && 
          <Content style={{ background: "#FFF"}}>

            {page && 
            <CRUDPage name={page.name} tableName={page.table} tableColumns={page.table_columns} pkColumns={page.pk_columns ? page.pk_columns : null} allowedActions={page.allowed_actions} versioned={page.versioned ? page.versioned : false} isRepo={page.datasource === "repo" ? "true" : "false"} lookups={getLookups(page.table_columns)} token={token}/>
            }

          </Content>
          }
        </Layout>
      </Layout>
      );

};

export default CRUDApp;

