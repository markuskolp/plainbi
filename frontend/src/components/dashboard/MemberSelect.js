import React from "react";
import { useCubeQuery } from "@cubejs-client/react";
import { useState, useEffect } from "react";
import { Typography, Select } from "antd";
const { Text } = Typography;

const MemberSelect = ({onChange}) => {

    const [resultSet, setResultSet] = useState([]); // metadata of all apps
  
    console.log("MemberSelect");
  
    useEffect(() => {
        console.log("MemberSelect - useEffect");
    }, [resultSet]);
  
    const init = async () => {
    };

    const query = {
        "order": [
        [
            "Veranstaltung.veranstaltungJahr",
            "desc"
        ],
        [
            "Veranstaltung.veranstaltungName",
            "asc"
        ]
        ],
        "segments": [
        "Ticket.onlineBestellungen"
        ],
        "dimensions": [
        "Veranstaltung.veranstaltungJahr",
        "Veranstaltung.veranstaltungName"
        ],
        "filters": [
        {
            "member": "Veranstaltung.veranstaltungJahr",
            "operator": "gte",
            "values": [
            "2022"
            ]
        },
        {
            "member": "Veranstaltung.veranstaltungName",
            "operator": "notContains",
            "values": [
            "Complimentary Card","Ticketshop"
            ]
        }
        ],
        "limit": 5000
    };

    //setResultSet(useCubeQuery(query));
    const renderProps = useCubeQuery(query); // const { resultSet, isLoading, error, progress }

    console.log("MemberSelect - renderProps");
    console.log(renderProps);
    /*
    console.log("resultSet.tablePivot()");    
    console.log(renderProps.resultSet.tableColumns({
        x: [],
        y: ['Veranstaltung.veranstaltungJahr', 'Veranstaltung.veranstaltungName', 'measures']
      }))
    ;
    */

    const handleChange = (name, option) => {
        //const emuEvent = { "target": { "name": name, "value": value}} // emulate event.target.name/.value object
        //console.log("MemberSelect change: " + JSON.stringify(emuEvent));
        console.log("option: ");
        console.log(option); 
        console.log(option.key);
        onChange(option.key);
      };

    return (
        <Select
            placeholder="bitte auswählen ..."
            allowClear
            showSearch
            size='small'
            disabled={false}
            defaultValue={'EXPO REAL 2023'}
            onChange={handleChange}
            //onSearch={onSearch}
            name={'va'}
            style={{ minWidth: 250 }}
            optionFilterProp="label" // filter by label (not by value/key)
            >
            {renderProps.resultSet && renderProps.resultSet.tablePivot().map((data) => (
                <Select.Option key={data["Veranstaltung.veranstaltungName"]} value={data["Veranstaltung.veranstaltungName"]} label={data["Veranstaltung.veranstaltungName"]} />
            ))}
        </Select>
    )

};


export default MemberSelect;

/*
    -- zuerst gruppiert nach Jahren und erst danach die Veranstaltungen in Select darstellen
    -- t.b.d.
            {renderProps.resultSet && renderProps.resultSet.tableColumns({
                                                                            x: [],
                                                                            y: ['Veranstaltung.veranstaltungJahr', 'Veranstaltung.veranstaltungName', 'measures']
                                                                        }).map((data) => (

    -- nur Veranstaltungen als einfache Select darstellen
            {renderProps.resultSet && renderProps.resultSet.tablePivot().map((data) => (
                <Select.Option key={data["Veranstaltung.veranstaltungName"]} value={data["Veranstaltung.veranstaltungName"]} label={data["Veranstaltung.veranstaltungName"]} />
            ))}

    console.log("resultSet.tableColumns(pivotConfig)");    
    console.log(renderProps.resultSet.tableColumns(pivotConfig));

    const pivotConfig = {
        "x": [
          "Veranstaltung.veranstaltungJahr"
        ],
        "y": [
          "Veranstaltung.veranstaltungName"
        ],
        "fillMissingDates": true,
        "joinDateRange": false,
        "limit": 5000
      };

<Select
        mode="multiple"
        style={{ width: '100%' }}
        placeholder="Please select"
        onSelect={(measure) => updateMeasures.add(measure)}
        onDeselect={(measure) => updateMeasures.remove(measure)}
    >
        {availableMeasures.map((measure) => (
        <Select.Option key={measure.name} value={measure}>
            {measure.title}
        </Select.Option>
        ))}
    </Select>
    */