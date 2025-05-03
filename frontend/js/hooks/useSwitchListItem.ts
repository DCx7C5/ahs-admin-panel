import { useState } from "react";

// Define generic interfaces for the hook
interface Item {
  id: string | number;
  [key: string]: any;
}

interface UseSwitchListItemProps<T extends Item> {
  uniqueId: string;
  itemList: T[];
}

interface UseSwitchListItemReturn<T extends Item> {
  items: T[];
  handleAddItem: (newItem?: T) => void;
  handleDeleteItem: (id: string | number) => void;
  handleSwitchItems: (index1: number, index2: number) => void;
}

/**
 * Helper function to add an item to array
 */
const addItem = <T extends Item>(items: T[], newItem: T): T[] => {
  return [...items, newItem];
};

/**
 * Helper function to remove an item from array by id
 */
const removeItem = <T extends Item>(items: T[], id: string | number): T[] => {
  return items.filter(item => item.id !== id);
};

/**
 * Helper function to switch positions of two items in array
 */
const switchItems = <T>(items: T[], index1: number, index2: number): T[] => {
  // Create a new array to avoid mutating the original
  const newItems = [...items];
  
  // Make sure indices are valid
  if (index1 < 0 || index1 >= items.length || index2 < 0 || index2 >= items.length) {
    return newItems;
  }
  
  // Swap the items
  [newItems[index1], newItems[index2]] = [newItems[index2], newItems[index1]];
  
  return newItems;
};

/**
 * A custom hook to manage list items with add, delete, and switch functionality
 * @template T - Type of list items, must extend Item interface
 * @param props - Object containing uniqueId and itemList
 * @returns Object with items array and handler functions
 */
const useSwitchListItem = <T extends Item>({ uniqueId, itemList }: UseSwitchListItemProps<T>): UseSwitchListItemReturn<T> => {
  const [items, setItems] = useState<T[]>(itemList);

  // Add an item to the array
  const handleAddItem = (newItem?: T) => {
    if (newItem) {
      setItems((prevItems) => addItem(prevItems, newItem));
    } else {
      // Create a default item if none provided - this is just a placeholder, 
      // in real usage you would use a proper item factory function
      const defaultItem = {
        id: `${uniqueId}_${Date.now()}`,
        name: `Item ${items.length + 1}`
      } as T;
      
      setItems((prevItems) => addItem(prevItems, defaultItem));
    }
  };

  // Delete an item from the array
  const handleDeleteItem = (id: string | number) => {
    setItems((prevItems) => removeItem(prevItems, id));
  };

  // Switch two items in the array
  const handleSwitchItems = (index1: number, index2: number) => {
    setItems((prevItems) => switchItems(prevItems, index1, index2));
  };

  return {
    items,
    handleAddItem,
    handleDeleteItem,
    handleSwitchItems
  };
};

export default useSwitchListItem;
