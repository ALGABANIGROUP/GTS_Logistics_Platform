import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { API_BASE_URL } from "../config/env";

const API_ROOT = String(API_BASE_URL || "").replace(/\/+$/, "");

const EmailList = ({ onSelect }) => {
  const [emails, setEmails] = useState([]);

  useEffect(() => {
    fetch(`${API_ROOT}/api/emails`)
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
