import React from "react";
import { Typography, DatePicker } from "antd";
import dayjs from 'dayjs';
const { RangePicker } = DatePicker;


const DateRange = ({columnId, onChange}) => {

    console.log("DateRange");
    console.log("DateRange - columnId: " + columnId);

    const rangePresets = [
      { label: 'Letzte 7 Tage', value: [dayjs().add(-7, 'd'), dayjs()] },
      { label: 'Letzte 14 Tage', value: [dayjs().add(-14, 'd'), dayjs()] },
      { label: 'Letzte 30 Tage', value: [dayjs().add(-30, 'd'), dayjs()] },
      { label: 'Letzte 90 Tage', value: [dayjs().add(-90, 'd'), dayjs()] },
    ];
    
    const onRangeChange = (dates, dateStrings) => {
      if (dates) {
        console.log('From: ', dates[0], ', to: ', dates[1]);
        console.log('From: ', dateStrings[0], ', to: ', dateStrings[1]);
      } else {
        console.log('Clear');
      }
      onChange(columnId, dateStrings); // filterName, filterValue [0] = from, [1] = to
    };

    return (
        <RangePicker 
          size='small' 
          //defaultValue={[dayjs().add(-30, 'd'), dayjs()]} 
          presets={rangePresets} 
          onChange={onRangeChange} 
          allowEmpty={[true, true]}
        />
    )

};

export default DateRange;
