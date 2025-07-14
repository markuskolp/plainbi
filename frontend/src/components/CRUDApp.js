import React from "react";
import { useState, useEffect } from "react";
import { Layout,  Menu, message, Typography, Alert} from "antd";
import LoadingMessage from "./LoadingMessage";
import CRUDPage from "./CRUDPage";
import NoPage from "../pages/NoPage";
const { Header, Content, Sider } = Layout;
const { Link } = Typography;

//TODO: setPageNotFound geht unten nicht (Zeile 33 und 47), weil es dann eine Endlosschleife ist -> rausfinden wie man es behebt

const CRUDApp = ({ name, alias, datasource, pages, token, start_page_id, record_pk }) => {
  
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);

  const [pageNotFound, setPageNotFound] = useState(false);
  const [selectedPage, setSelectedPage] = useState(null); // nr of selected page
    const [page, setPage] = useState(); // page metadata
    const [pageList, setPageList] = useState(); // page metadata
    console.log("selectedPage: " + selectedPage);
    //console.log("start_page_id: " + start_page_id);

    //console.log("datasource:" + datasource);
    
    useEffect(() => {
      setSelectedPage(getPageId(start_page_id ? start_page_id : 1).toString()); 
      setPageList(pages.map((page) => {
          // check if page should be hidden from navigation
          let pageHide = false;
          if (page.hide_in_navigation && page.hide_in_navigation == 'true') {
            pageHide = true;
          }
          console.log("CRUD / pages: " + page.name + ' - ' + page.id + ' - hide: ' + pageHide);
          return pageHide ? '' : getItem(<Link href={'/apps/'+alias+'/'+page.alias}>{page.name}</Link>, page.id); // return pages without the ones that should be hidden
        })
      );  
      setLoading(false);
    }, []);

    // getPageID: either the ID is a number and stays as it is - or - it is a ALIAS and the page id is retrieved
    function getPageId(page_id) {
      let page_id_type = Number.isNaN(page_id * 1) ? "alias" : "id"; // check whether the "id" refers to the real "id" or its "alias"
      console.log("CRUDApp - getPageId - page_id_type: " + page_id_type);
      let found_page_id = 1;
      if(page_id_type == 'alias') {
        console.log("CRUDApp - getPageId - search for ID with alias");
        found_page_id = pages.filter((page) => page.alias == page_id).map((page) => {
          return page.id // return real page id when the alias was found in all pages
        })
        console.log(found_page_id.length);
        if (found_page_id.length < 1) { 
          console.log("CRUDApp - getPageId - not found"); 
          setPageNotFound(true);
          console.log(error);
        } else {
          console.log("CRUDApp - getPageId - found_page_id: " + found_page_id);
        }
      } else {
        console.log("CRUDApp - getPageId - ID is number, search for it");
        found_page_id = pages.filter((page) => page.id == page_id).map((page) => {
          return page.id // return real page id when the alias was found in all pages
        })
        console.log(found_page_id.length);
        if (found_page_id.length < 1) { 
          console.log("CRUDApp - getPageId - not found"); 
          setPageNotFound(true);
          console.log(error);
        } else {
          console.log("CRUDApp - getPageId - found_page_id: " + found_page_id);
        }
      }
      found_page_id = (found_page_id ? found_page_id : 1);
      setPage(pages[found_page_id-1]); // get found page or default page (the first = 1-1)
      return found_page_id;
    }

    // Layout settings
    const [mode, setMode] = useState("inline");
    const [theme, setTheme] = useState("light");

    // Switch page
    const switchPage = (e) => {
      /*const pageIndex = e.key - 1;
      console.log('switchPage() - set page to id: ' + e.key + ' = pageIndex: ' + pageIndex);
      setSelectedPage(e.key);
      setPage(pages[pageIndex]);
      */
     // do nothing, because see useEffect() - setPageList() - the Link does its job there
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
        loading ? (
          <LoadingMessage />
        ) : (
          pageNotFound === true ? (
            <NoPage />
          ) : (
            <Layout className="layout">
              <Header className="pageheader">{name}</Header>
              <Layout>
                {pages.length > 1 && // show only the sider menu (page list) when more than 1 page is listed
                <Sider max-width={250} theme={theme} collapsible  breakpoint="lg" collapsedWidth="0" onBreakpoint={broken => {console.log(broken);}} onCollapse={(collapsed, type) => {console.log(collapsed, type);}} >
                  <Menu
                    style={{ maxWidth: 250 }} //, marginTop: "25px"
                    defaultSelectedKeys={selectedPage}
                    defaultOpenKeys={selectedPage}
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
                    <CRUDPage key={page.name} name={page.name} tableName={page.table} tableForList={page.table_for_list} tableColumns={page.table_columns} pkColumns={page.pk_columns ? page.pk_columns : null} userColumn={page.user_column ? page.user_column : null} defaultOrderBy={page.order ? page.order : null} allowedActions={page.allowed_actions} externalActions={page.external_actions} conditionalRowFormats={page.conditional_row_formats} versioned={page.versioned ? page.versioned : false} datasource={datasource} isRepo={(datasource == "repo" || datasource == "0") ? "true" : "false"} lookups={getLookups(page.table_columns)} token={token} sequence={page.sequence ? page.sequence : null} breadcrumbItems={(page.show_breadcrumb && page.show_breadcrumb === 'true') ? [{title:page.parent_page.name, href:'/apps/'+alias+'/'+page.parent_page.alias}, {title:page.name}] : null} />
                    // key property resets state when changed - this is important for page switch (to reset filter, order, offset and limit in page component)!
                    }

                  </Content>
                  }
              </Layout>
            </Layout>
          )
        )
    );

};

export default CRUDApp;
