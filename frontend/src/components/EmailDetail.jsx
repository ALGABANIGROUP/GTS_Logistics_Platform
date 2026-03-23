import PropTypes from 'prop-types';

const EmailDetail = ({ email }) => {
  if (!email) {
    return <div className="text-gray-500">Select an email to view details.</div>;
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-xl font-bold">{email.subject}</h3>
        <p className="text-sm text-gray-600">{email.timestamp}</p>
      </div>
      <div>
        <h4 className="font-semibold">From:</h4>
        <p>{email.from_}</p>
      </div>
      <div>
        <h4 className="font-semibold">Message:</h4>
        <pre className="whitespace-pre-wrap">{email.body}</pre>
      </div>
      <div>
        <h4 className="font-semibold">Reply Sent:</h4>
        <pre className="whitespace-pre-wrap">{email.reply}</pre>
      </div>
    </div>
  );
};

EmailDetail.propTypes = {
  email: PropTypes.shape({
    subject: PropTypes.string.isRequired,
    timestamp: PropTypes.string.isRequired,
    from_: PropTypes.string.isRequired,
    body: PropTypes.string.isRequired,
    reply: PropTypes.string,
  }),
};

export default EmailDetail;
