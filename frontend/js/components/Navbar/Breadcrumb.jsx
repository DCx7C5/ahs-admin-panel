import React from 'react';
import PropTypes from 'prop-types';

const Breadcrumb = ({ items, separator = '/' }) => {
  return (
    <nav aria-label="breadcrumb">
      <ol style={styles.breadcrumb}>
        {items.map((item, index) => (
          <li
            key={index}
            style={{
              ...styles.breadcrumbItem,
              ...(index === items.length - 1 ? styles.activeItem : {}),
            }}
            aria-current={index === items.length - 1 ? 'page' : undefined}
          >
            {item.link ? (
              <a href={item.link} style={styles.link}>
                {item.label}
              </a>
            ) : (
              <span>{item.label}</span>
            )}
            {index < items.length - 1 && (
              <span style={styles.separator}>{separator}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

Breadcrumb.propTypes = {
  /**
   * An array of items for the breadcrumb.
   * Each item is an object with `label` (required) and `link` (optional).
   */
  items: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      link: PropTypes.string, // Optional link
    })
  ).isRequired,
  /**
   * Separator to display between breadcrumb items. Default is '/'.
   */
  separator: PropTypes.string,
};

// Basic styles for this component
const styles = {
  breadcrumb: {
    listStyle: 'none',
    display: 'flex',
    padding: 0,
    margin: 0,
  },
  breadcrumbItem: {
    display: 'flex',
    alignItems: 'center',
    fontSize: '1rem',
    color: '#6c757d', // Bootstrap gray
  },
  activeItem: {
    fontWeight: 'bold',
    color: '#212529', // Bootstrap dark
  },
  link: {
    color: '#007bff', // Bootstrap blue
    textDecoration: 'none',
  },
  separator: {
    margin: '0 0.5rem',
  },
};

export default Breadcrumb;