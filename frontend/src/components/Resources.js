import React from "react";
import { useState, useEffect } from "react";
import { Card, Tooltip, Table, Tag, Alert, Flex, Space, Breadcrumb } from "antd";
import {
  AppstoreOutlined,
  FileExcelFilled,
  FileTextFilled,
  TableOutlined,
  DashboardOutlined,
  FileUnknownOutlined, TeamOutlined
} from "@ant-design/icons";
import { Avatar, Layout } from "antd";
import { Typography } from 'antd';
import { PageHeader } from "@ant-design/pro-layout";
import LoadingMessage from "./LoadingMessage";
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";
import { extractResponseData, sortByName } from "../utils/dataUtils";

const { Title, Link, Text } = Typography;

const contact_email = window.CONTACT_EMAIL;

const Resources = (props) => {

  const { loading, setLoading, error, setApiError } = useApiState(true);
  const [resources, setResources] = useState([]);
  const [groups, setGroups] = useState([]);
  const [selectedGroupID, setSelectedGroupID] = useState(null);
  const [selectedGroupName, setSelectedGroupName] = useState();
  const [selectedCategory, setSelectedCategory] = useState();
  const [availableCategories, setAvailableCategories] = useState();

  useEffect(() => {
    setSelectedCategory("all");
    setAvailableCategories([
      { value: "all", label: "Alle" },
      { value: "ext", label: "Bericht/Dashboard" },
      { value: "adh", label: "Adhoc" },
      { value: "app", label: "Applikation" }
    ]);
    apiClient.get("/api/repo/groups")
      .then((res) => {
        setGroups(sortByName(extractResponseData(res)));
        setLoading(false);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der berechtigten Ressourcen.', err));
  }, []);

  const refreshGroupData = async (groupID) => {
    setResources([]);
    setLoading(true);
    apiClient.get("/api/repo/group/" + groupID + "/resources")
      .then((res) => {
        setResources(sortByName(extractResponseData(res)));
        setLoading(false);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der berechtigten Ressourcen.', err));
  };

  const columns = [
    {
      title: " ",
      dataIndex: "output_format",
      key: "output_format",
      width: 50,
      render: (outputformat, record) => (
        record.resource_type === "external_resource" ? <DashboardOutlined /> : (
          record.resource_type === "application" ? <AppstoreOutlined /> : (
            outputformat === "XLSX" ? <FileExcelFilled style={{ color: '#1D6F42' }} /> : (
              outputformat === "CSV" ? <FileTextFilled style={{ color: '#0055b3' }} /> : (
                outputformat === "HTML" ? <TableOutlined /> : <FileUnknownOutlined />
              )
            )
          )
        )
      )
    },
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      sorter: (a, b) => (a.name > b.name ? 1 : -1),
      width: 500,
      render: (name, record) => (
        <Tooltip title={record.description}>
          <Link href={record.url} target={record.target ? record.target : ""}>{name}</Link>
        </Tooltip>
      )
    },
    {
      title: "Typ",
      dataIndex: "resource_type_de",
      key: "resource_type_de",
      width: 100,
      render: (name, record) => (
        record.resource_type_de && <Tag color="blue" style={{ textTransform: 'uppercase' }}>{record.resource_type_de}</Tag>
      )
    }
  ];

  const handleGroupChange = (groupID, groupName, e) => {
    setSelectedGroupID(groupID);
    setSelectedGroupName(groupName);
    refreshGroupData(groupID);
  };

  const resetGroupID = (e) => {
    e.preventDefault();
    setSelectedGroupID(null);
  };

  return (
    <React.Fragment>
      <Space direction="vertical" size="middle">
        <PageHeader title="Berechtigte Inhalte" subTitle="" />
        {loading ? (
          <LoadingMessage />
        ) : (
          selectedGroupID > 0 ? (
            <React.Fragment>
              <Breadcrumb>
                <Breadcrumb.Item href='' onClick={(e) => { resetGroupID(e); }}>
                  <TeamOutlined /><span>Gruppen</span>
                </Breadcrumb.Item>
                <Breadcrumb.Item>{selectedGroupName}</Breadcrumb.Item>
              </Breadcrumb>
              <Table
                pagination={false}
                size="middle"
                columns={columns}
                dataSource={resources && selectedCategory && resources.filter((row) => ("all" == selectedCategory || row.resource_type_de.substring(0, 3).toLowerCase() == selectedCategory.toLowerCase()))}
                loading={loading}
                rowKey="id"
              />
            </React.Fragment>
          ) : (
            <React.Fragment>
              <Flex gap="middle" wrap>
                {groups && groups.map((group) => (
                  <Tooltip key={group.id} title={group.name}>
                    <Link onClick={(e) => { handleGroupChange(group.id, group.name, e); }}>
                      <Card style={{ maxWidth: 300, minWidth: 300 }} bordered hoverable>
                        <Card.Meta
                          avatar={
                            <Avatar
                              icon={<TeamOutlined />}
                              style={{ backgroundColor: '#fff', color: '#000', marginTop: '-5px' }}
                            />
                          }
                          title={group.name}
                        />
                      </Card>
                    </Link>
                  </Tooltip>
                ))}
              </Flex>
              {groups.length < 1 &&
                <Alert
                  message="Hinweis"
                  description={
                    <React.Fragment>
                      <Text>Du bist bisher nicht für irgendwelche Inhalte berechtigt. Bitte wende dich an </Text>
                      {contact_email ?
                        <Link href={'mailto:' + contact_email}>{contact_email}</Link> :
                        <Text>das zuständige Team.</Text>
                      }
                    </React.Fragment>
                  }
                  type="info"
                  showIcon
                />
              }
            </React.Fragment>
          )
        )}
      </Space>
    </React.Fragment>
  );
};

export default Resources;
