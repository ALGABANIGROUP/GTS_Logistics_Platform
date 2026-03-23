import { useEffect, useState } from "react";
import PropTypes from "prop-types";

const EmailList = ({ onSelect }) => {
  const [emails, setEmails] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/emails")
      .then((res) => res.json())
      .then((data) => setEmails(data.reverse()));
  }, []);

  return (
    <div className="space-y-4">
      {emails.map((email, index) => (
        <div
          key={index}
          className="cursor-pointer border p-2 rounded shadow hover:bg-gray-100"
          onClick={() => onSelect(email)}
        >
          <div className="text-sm text-gray-500">{email.timestamp}</div>
          <div className="font-bold">{email.subject}</div>
          <div className="text-sm truncate">{email.reply}</div>
        </div>
      ))}
    </div>
  );
};

EmailList.propTypes = {
  onSelect: PropTypes.func.isRequired,
};

export default EmailList;
