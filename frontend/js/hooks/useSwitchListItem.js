import React, {useState} from "react";




const useSwitchListItem = ({uniqueId, itemList}) => {
  const [items, setItems] = useState(itemList);

    // Add an item to the array
  const handleAddItem = () => {
    setItems((prevItems) => addItem(prevItems, `Item ${prevItems.length + 1}`));
  };

  // Delete an item from the array
  const handleDeleteItem = (uniqueId) => {
    setItems((prevItems) => removeItem(prevItems, index));
  };

  // Switch two items in the array
  const handleSwitchItems = (index1, index2) => {
    setItems((prevItems) => switchItems(prevItems, index1, index2));
  };


}