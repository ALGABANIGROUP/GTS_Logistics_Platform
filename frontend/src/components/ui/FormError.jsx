import React from "react";

export default function FormError({ message, className = "" }) {
  if (!message) return null;
  return (
    <p className={`text-sm text-red-200 ${className}`.trim()} role="alert">
      {message}
    </p>
  );
}
