import {useCallback, useState} from "react";



const useList = (initialItems = []) => {
  const [items, setItems] = useState(initialItems);

  // Add a new item to the list
  const addItem = useCallback((item) => {
    setItems((prevItems) => [...prevItems, item]);
  }, []);

  // Remove an item from the list by its ID
  const removeItem = useCallback((id) => {
    setItems((prevItems) => prevItems.filter((item) => item.id !== id));
  }, []);

  // Update an existing item by its ID
  const updateItem = useCallback((id, newItemData) => {
    setItems((prevItems) =>
      prevItems.map((item) => (item.id === id ? { ...item, ...newItemData } : item))
    );
  }, []);

  // Reorder items (e.g., for drag-and-drop functionality)
  const reorderItems = useCallback((startIndex, endIndex) => {
    setItems((prevItems) => {
      const result = [...prevItems];
      const [removed] = result.splice(startIndex, 1);
      result.splice(endIndex, 0, removed);
      return result;
    });
  }, []);

  return [items, { addItem, removeItem, updateItem, reorderItems }];
};

export default useList;