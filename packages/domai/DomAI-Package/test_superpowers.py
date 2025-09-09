#!/Library/Developer/CommandLineTools/usr/bin/python3
"""
Test DominateAI Superpowers
"""

import sys
from pathlib import Path

# Add DominateAI to path
sys.path.insert(0, str(Path(__file__).parent))

from superpower_manager import SuperpowerManager

def test_superpowers():
    """Test superpower initialization"""
    
    print("🚀 Testing DominateAI Superpowers")
    print("=" * 50)
    
    try:
        # Initialize SuperpowerManager
        manager = SuperpowerManager()
        
        # Initialize all superpowers
        powers = manager.initialize_all_superpowers()
        
        print(f"\n✨ Successfully loaded {len(powers)} superpowers!")
        
        # List all superpowers
        print("\n⚡ Available Superpowers:")
        for name in manager.list_superpowers():
            print(f"  • {name}")
        
        # Test a specific superpower
        mac_control = manager.get_superpower('Mac System Control')
        if mac_control:
            print("\n🖥️  Testing Mac Control:")
            info = mac_control.get_system_info()
            print(f"  • System: {info.get('os_version', 'Unknown')}")
            print(f"  • User: {info.get('username', 'Unknown')}")
            print(f"  • Architecture: {info.get('architecture', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing superpowers: {e}")
        return False

if __name__ == "__main__":
    success = test_superpowers()
    
    if success:
        print("\n🎉 DominateAI Superpowers are ready!")
        print("💡 Run './domai' and try commands like:")
        print("   • superpowers")
        print("   • system info") 
        print("   • build website for my portfolio")
        print("   • open application Safari")
    else:
        print("\n❌ Superpowers test failed")