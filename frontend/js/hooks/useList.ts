import { useCallback, useState } from "react";

// Define the item structure with a required id property
interface ListItem {
  id: string | number;
  [key: string]: any;
}

// Define the operations available on the list
interface ListOperations<T extends ListItem> {
  addItem: (item: T) => void;
  removeItem: (id: string | number) => void;
  updateItem: (id: string | number, newItemData: Partial<T>) => void;
  reorderItems: (startIndex: number, endIndex: number) => void;
}

// Define the return type of the hook
type UseListReturn<T extends ListItem> = [T[], ListOperations<T>];

const useList = <T extends ListItem>(initialItems: T[] = []): UseListReturn<T> => {
  const [items, setItems] = useState<T[]>(initialItems);

  // Add a new item to the list
  const addItem = useCallback((item: T): void => {
    setItems((prevItems) => [...prevItems, item]);
  }, []);

  // Remove an item from the list by its ID
  const removeItem = useCallback((id: string | number): void => {
    setItems((prevItems) => prevItems.filter((item) => item.id !== id));
  }, []);

  // Update an existing item by its ID
  const updateItem = useCallback((id: string | number, newItemData: Partial<T>): void => {
    setItems((prevItems) =>
      prevItems.map((item) => (item.id === id ? { ...item, ...newItemData } : item))
    );
  }, []);

  // Reorder items (e.g., for drag-and-drop functionality)
  const reorderItems = useCallback((startIndex: number, endIndex: number): void => {
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
