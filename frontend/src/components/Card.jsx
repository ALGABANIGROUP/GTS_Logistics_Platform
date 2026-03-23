// frontend/src/components/Card.jsx
import React from "react";

const Card = ({ title, description, icon, onClick }) => {
    return (
        <div
            onClick={onClick}
            className="cursor-pointer rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md"
        >
            {/* Icon */}
            {icon && (
                <div className="mb-3 text-3xl">
                    {icon}
                </div>
            )}

            {/* Title */}
            <h3 className="text-base font-semibold text-slate-900">
                {title}
            </h3>

            {/* Description */}
            {description && (
                <p className="mt-1 text-sm text-slate-600">
                    {description}
                </p>
            )}
        </div>
    );
};

export default Card;
