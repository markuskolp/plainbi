import React from 'react';
import LoadingMessage from './LoadingMessage';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import moment from 'moment';
import 'moment/locale/de';
import { Calendar, momentLocalizer } from 'react-big-calendar';

moment.locale('de');

const CalendarMessages = {
  today: 'Heute', previous: 'Zurück', next: 'Weiter', month: 'Monat',
  week: 'Woche', day: 'Tag', agenda: 'Agenda', date: 'Datum',
  time: 'Uhrzeit', event: 'Termin', noEventsInRange: 'Keine Termine in diesem Zeitraum.',
};

const EventWithTwoColumns = ({ event }) => (
  <a href={event.url} target="_blank" rel="noopener noreferrer"
    style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', width: '100%', height: '100%', textDecoration: 'none', color: 'inherit', padding: '2px' }}>
    <span style={{ flex: '1 1 auto', minWidth: 0 }}>{event.title}</span>
    <span style={{ fontSize: '0.85em', flex: '1 1 auto', minWidth: 0 }}>{event.subtitle}</span>
  </a>
);

const eventStyleGetter = (event) => ({
  style: { backgroundColor: event.color || '#007bff', color: 'white', borderRadius: '4px', padding: '2px 4px', cursor: 'pointer' }
});

export const parseDateString = (str, dayAdd = 0) => {
  try {
    const [year, month, day] = str.split("-").map(Number);
    const date = new Date(year, month - 1, day + dayAdd);
    return isNaN(date.getTime()) ? null : date;
  } catch (er) { return null; }
};

const CRUDCalendar = ({ loading, calendarData }) => (
  <div className="height600">
    {loading ? <LoadingMessage /> : (
      <Calendar
        defaultDate={new Date()}
        events={calendarData}
        localizer={momentLocalizer(moment)}
        showMultiDayTimes
        step={60}
        views={{ month: true }}
        messages={CalendarMessages}
        components={{ event: EventWithTwoColumns }}
        eventPropGetter={eventStyleGetter}
        popup
      />
    )}
  </div>
);

export default CRUDCalendar;
